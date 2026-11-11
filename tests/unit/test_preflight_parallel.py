import asyncio
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from chupa.llm import LLMRequest
from chupa.providers import ProviderLLM


class MemoryFS:
    def write(self, path, data):
        pass


class Session:
    def __init__(self):
        self.thresh = NS(configure=lambda config: None)
        self.passed = 0

    def exclusions(self):
        return set()

    def preflight_passed(self):
        self.passed += 1


def make_client(exec_):
    def provider(name):
        return NS(name=name, package=f"{name}-pkg", auth=None, base_url=None, limits=NS(est_cost_per_call_usd=1), models_by_tier=NS(low="unused"))

    providers = [provider("claude"), provider("codex")]
    candidates = [NS(provider="codex", model="one"), NS(provider="claude", model="two"), NS(provider="codex", model="three")]
    config = NS(providers=providers, routing=[NS(tier="low", candidates=candidates)], state_dir=Path("/state"))
    session = Session()
    return ProviderLLM(config, exec_=exec_, fs=MemoryFS(), env={}, cwd=Path("/repo"), timeout=10, session=session)


class ProbeExec:
    def __init__(self, refused=(), reverse=False):
        self.refused, self.reverse = refused, reverse
        self.calls = []
        self.started = asyncio.Event()
        self.release = [asyncio.Event() for _ in range(3)]
        self.release[-1].set()
        self.finished = []

    async def run(self, argv, **kwargs):
        self.calls.append(list(argv))
        if argv[1:] == ["--version"]:
            return 0, "1.0.0", ""
        if argv[0] == "pnpm":
            return 0, "2.0.0", ""
        model = argv[argv.index("--model" if argv[0] == "claude" else "-m") + 1]
        index = ["one", "two", "three"].index(model)
        if len(self.calls) == 7:
            self.started.set()
        await self.started.wait()
        if self.reverse:
            await self.release[index].wait()
            if index:
                self.release[index - 1].set()
        self.finished.append(model)
        if model in self.refused:
            return 1, "", f"refused {model}"
        event = {"type": "result", "subtype": "success", "result": "ok", "total_cost_usd": 1} if argv[0] == "claude" else {"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}}
        return 0, json.dumps(event), ""


@pytest.mark.asyncio
async def test_all_probes_start_before_any_finishes():
    exec_ = ProbeExec()
    client = make_client(exec_)
    assert await asyncio.wait_for(client.preflight(), 2) == []
    assert client.session.passed == 1
    assert [call[:2] for call in exec_.calls[:4]] == [["claude", "--version"], ["pnpm", "view"], ["codex", "--version"], ["pnpm", "view"]]
    assert [call[0] for call in exec_.calls[4:]] == ["codex", "claude", "codex"]


@pytest.mark.asyncio
async def test_results_and_notices_keep_routing_and_adapter_order():
    exec_ = ProbeExec(refused={"one", "three"}, reverse=True)
    client = make_client(exec_)
    problems = await asyncio.wait_for(client.preflight(), 2)
    assert exec_.finished == ["three", "two", "one"]
    assert len(problems) == 2 and "model 'one'" in problems[0] and "model 'three'" in problems[1]
    assert client.session.passed == 0
    assert [notice.split()[0] for notice in client.preflight_notices] == ["claude", "codex"]


@pytest.mark.asyncio
async def test_abort_kills_all_concurrent_groups_and_calls_remove_them():
    class RunningExec:
        def __init__(self):
            self.started = asyncio.Event()
            self.release = asyncio.Event()
            self.groups = []
            self.killed = []

        async def run(self, argv, **kwargs):
            group = 101 + len(self.groups)
            self.groups.append(group)
            kwargs["on_spawn"](group)
            if len(self.groups) == 2:
                self.started.set()
            await self.release.wait()
            return 0, json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}}), ""

        def kill_group(self, group):
            self.killed.append(group)

    exec_ = RunningExec()
    adapter = make_client(exec_)._adapters["codex"]
    req = LLMRequest(surface="preflight", rendered="ok", tier="low", effort="low", ticket=None, worktree=None)
    tasks = [asyncio.create_task(adapter.invoke(req, model)) for model in ("one", "three")]
    await asyncio.wait_for(exec_.started.wait(), 2)
    assert adapter._pgids == {101, 102}
    adapter.abort()
    assert set(exec_.killed) == {101, 102}
    exec_.release.set()
    await asyncio.gather(*tasks)
    assert adapter._pgids == set()


@pytest.mark.asyncio
async def test_cancellation_waits_for_every_probe_to_unwind():
    class CancelExec(ProbeExec):
        def __init__(self):
            super().__init__()
            self.cleaning = []
            self.finish = asyncio.Event()

        async def run(self, argv, **kwargs):
            if argv[1:] == ["--version"] or argv[0] == "pnpm":
                return await super().run(argv, **kwargs)
            self.calls.append(list(argv))
            if len(self.calls) == 7:
                self.started.set()
            try:
                await asyncio.Event().wait()
            finally:
                self.cleaning.append(asyncio.current_task())
                await self.finish.wait()

    exec_ = CancelExec()
    client = make_client(exec_)
    task = asyncio.create_task(client.preflight())
    await asyncio.wait_for(exec_.started.wait(), 2)
    task.cancel()
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert len(exec_.cleaning) == 3 and not task.done()
    exec_.finish.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert all(child.done() for child in exec_.cleaning)
    assert client.session.passed == 0
