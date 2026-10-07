"""Drive the production CLI core through injected delivery, process, filesystem and time seams."""

import asyncio
import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from chupa import __main__ as cli, caps, daemon, driver, merge, providers, runner, stages
from chupa.config import ConfigError, ConfigSnapshot, load_config
from chupa.daemon import DaemonAdmission
from chupa.driver import Driver, LlmStage
from chupa.git import Git
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.mergequeue import CONFLICT_FACTS, MergeQueue
from chupa.providers import ProviderLLM, child_env
from chupa.redact import Redactor
from chupa.scheduler import Scheduler
from chupa.stages import StageContext
from chupa.tickets import INTAKE_SIGNAL
from chupa.watcher import WATCHER_PARSE_FAILURE, Watcher
from tests.test_cli import PLAN, write
from tests.test_daemon_admission import assert_idle
from tests.test_daemon_config import assert_detached, python_values
from tests.test_providers import CONFIG, ENV, claude_ok, codex_ok
from tests.test_scheduler import Time, import_closure, text, turn
from tests.test_mergequeue import ctx as admission_context, ready


class ScriptFS:
    def __init__(self):
        self.files = {}

    def write(self, path, data):
        self.files[path] = data

    def replace(self, src, dst):
        self.files[dst] = self.files.pop(src)


class ScriptExec:
    def __init__(self, fs):
        self.fs = fs
        self.calls = []
        self.hook = None
        self.latest = "1.2.3"
        self.reply = "ok"

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None, on_spawn=None):
        prompt = self.fs.files[stdin_path].decode() if stdin_path else None
        self.calls.append((list(argv), cwd, dict(env), prompt, timeout))
        if self.hook is not None:
            await self.hook(argv)
        if argv[1:] == ["--version"]:
            return 0, "1.2.3", ""
        if argv[0] == "pnpm":
            return 0, self.latest, ""
        assert argv[0] in {"claude", "codex"} and prompt is not None
        if on_spawn is not None:
            on_spawn(123)
        reply = "ok" if prompt == providers.PROBE_PROMPT else self.reply
        return 0, (claude_ok(reply) if argv[0] == "claude" else codex_ok(reply)), ""

    def kill_group(self, pgid):
        raise AssertionError("no scripted child survives its invocation")


class CoreRig:
    def __init__(self, root, *, prepare=None, config=CONFIG, config_path=None):
        self.root = root
        (root / "chupa").mkdir(exist_ok=True)
        (root / "chupa/thing.py").write_text("")
        self.config_path = config_path
        self.put_config(config)
        self.time = Time()
        self.fs = ScriptFS()
        self.exec = ScriptExec(self.fs)
        self.journal = Journal(root / "state", self.time)
        initial = load_config(config_path, cwd=root)
        self.checkout = runner.Checkout(
            root, initial, ENV, self.exec,
            Git(self.exec, env=child_env(ENV, initial), timeout=30),
            self.journal, self.fs, self.time, self.time.sleep,
        )
        self.files = {}
        self.quarantine, self.drought = set(), set()
        self.unmerged = 0
        self.calls, self.locals = [], []
        kwargs = {} if prepare is None else {"prepare": prepare}
        self.core = cli.build_daemon_core(
            self.checkout, config_path=config_path, plan=PLAN, read=self.files.get, debounce=5,
            quarantined=lambda: self.quarantine, drought_parked=lambda: self.drought,
            completed_unmerged=lambda: self.unmerged, **kwargs,
        )

    def put_config(self, config):
        (self.config_path or self.root / "config.yaml").write_text(config)

    async def publish(self, *stems):
        async def changes():
            for stem in stems:
                yield stem

        consumer = asyncio.create_task(self.core.watcher.run(changes()))
        await turn()
        await turn()
        self.time.advance(5)
        await consumer

    async def add(self, stem, priority="P2", state="confirmed", depends="none"):
        self.files[stem] = text(priority, state, depends)
        write(self.root, stem, self.files[stem])
        await self.publish(stem)
        return self.core.scheduler.pending[stem]

    def transition(self, stem, to, **body):
        self.journal.append(EventType.STATE_TRANSITION, {"to": to, **body}, ticket=stem)

    def intake(self, stem):
        self.journal.append(EventType.SIGNAL,
                            {"signal": INTAKE_SIGNAL, "source": "human", "state": "confirmed",
                             "new": True, "commit": "abc"}, ticket=stem)

    async def drain(self):
        while await self.core.scheduler.dispatch_next() is not None:
            pass


def assert_core_wiring(rig):
    core = rig.core
    assert isinstance(core.admission, DaemonAdmission)
    assert isinstance(core.scheduler, Scheduler) and isinstance(core.watcher, Watcher)
    assert core.scheduler.journal is core.watcher.journal is rig.checkout.journal
    assert core.scheduler.dispatch == core.admission.dispatch
    assert core.watcher.publish == core.scheduler.update
    assert core.watcher.remove == core.scheduler.remove
    assert core.watcher.read == rig.files.get and core.watcher.plan == PLAN
    assert core.watcher.clock is rig.checkout.clock and core.watcher.sleep == rig.checkout.sleep
    assert core.watcher.debounce == 5
    assert core.scheduler.max_unmerged == rig.checkout.config.scheduler.max_unmerged


@pytest.fixture
def rig(tmp_path):
    async def prepare(local):
        rig.locals.append(local)

        async def dispatch(ticket):
            rig.calls.append(ticket.stem)
            return "callback-owned-terminal"

        return dispatch

    rig = CoreRig(tmp_path, prepare=prepare)
    return rig


@pytest.mark.asyncio
async def test_production_root_builds_daemon_core_without_running_work(tmp_path, monkeypatch):
    async def prepare(_):
        raise AssertionError("prepared at construction")

    def forbid(*args, **kwargs):
        raise AssertionError("captured at construction")

    # Initial mutable checkout loading is separate from the root's per-admission loader.
    original = cli.load_config
    loads = []

    def load(*args, **kwargs):
        loads.append(args)
        return original(*args, **kwargs)

    monkeypatch.setattr(cli, "load_config", load)
    monkeypatch.setattr(daemon, "snapshot_config", forbid)
    tasks = asyncio.all_tasks()
    rig = CoreRig(tmp_path, prepare=prepare)
    assert_core_wiring(rig)
    assert_idle(rig.core.admission)
    assert not rig.core.scheduler.pending and rig.core.scheduler.active is None
    assert not rig.core.watcher.cache and not rig.core.watcher._waits
    assert loads == [] and rig.exec.calls == [] and rig.fs.files == {}
    assert rig.journal.read() == [] and asyncio.all_tasks() == tasks


@pytest.mark.asyncio
async def test_production_core_dispatches_through_admission_and_snapshot(tmp_path):
    called = []

    async def prepare(local):
        assert local is not rig.checkout
        assert isinstance(local.config, ConfigSnapshot)
        assert_detached(rig.checkout.config, local.config)
        for field in ("repo", "env", "exec_", "git", "journal", "fs", "clock", "sleep"):
            assert getattr(local, field) is getattr(rig.checkout, field)
        called.append(local)

        async def callback(original):
            assert original is ticket
            assert rig.core.admission.active is original
            assert rig.core.admission.task is asyncio.current_task()
            with pytest.raises(AttributeError):
                local.config.caps.retry = 99
            return "original-terminal"

        return callback

    rig = CoreRig(tmp_path, prepare=prepare)
    ticket = await rig.add("work")
    assert await rig.core.scheduler.dispatch(ticket) == "original-terminal"
    assert len(called) == 1 and rig.journal.read() == []
    assert_idle(rig.core.admission)


@pytest.mark.asyncio
@pytest.mark.parametrize("new_ticket", [False, True])
async def test_production_core_reprioritizes_without_preemption(tmp_path, new_ticket):
    started, release, cleaning, finish = (asyncio.Event() for _ in range(4))
    calls = []

    async def prepare(local):
        async def callback(ticket):
            calls.append(ticket.stem)
            if ticket.stem == "active":
                try:
                    started.set()
                    await release.wait()
                finally:
                    cleaning.set()
                    await finish.wait()
            return "merged"
        return callback

    rig = CoreRig(tmp_path, prepare=prepare)
    for stem, priority in (("active", "P0"), ("normal", "P1"), ("urgent", "P3")):
        await rig.add(stem, priority)
    first = asyncio.create_task(rig.core.scheduler.dispatch_next())
    await started.wait()
    owned = rig.core.admission.task
    waiter = asyncio.create_task(rig.core.scheduler.dispatch_next())
    stem = "new-urgent" if new_ticket else "urgent"
    rig.files[stem] = text("P0")
    rig.core.watcher.change(stem)
    await turn()
    rig.time.advance(4)
    await turn()
    assert stem not in rig.core.scheduler.pending or rig.core.scheduler.pending[stem].frontmatter.priority == "P3"
    rig.time.advance(1)
    await turn()
    assert rig.core.scheduler.pending[stem].frontmatter.priority == "P0"
    release.set()
    await cleaning.wait()
    assert calls == ["active"] and not first.done() and not waiter.done()
    assert rig.core.scheduler.active is rig.core.admission.active
    assert rig.core.admission.task is owned and not owned.done()
    finish.set()
    assert (await first).stem == "active" and (await waiter).stem == stem
    assert calls == ["active", stem] and owned.done()
    assert_idle(rig.core.admission)
    assert rig.core.scheduler.active is None
    await rig.core.watcher.close()


@pytest.mark.asyncio
async def test_production_core_preserves_last_good_and_removes_tickets(rig):
    old = await rig.add("old", "P2")
    await rig.add("other", "P1")
    rig.files["old"] = text("P0").replace("- stuck: 20m", "- stuck: broken")
    rig.files["new-invalid"] = "partial"
    await rig.publish("old", "new-invalid")
    assert rig.core.watcher.cache["old"] is rig.core.scheduler.pending["old"] is old
    assert "new-invalid" not in rig.core.watcher.cache and "new-invalid" not in rig.core.scheduler.pending
    events = rig.journal.read()
    assert len(events) == 2
    for event, stem in zip(events, ("old", "new-invalid"), strict=True):
        assert event.type == EventType.SIGNAL and event.ticket == stem and event.key is None
        assert event.body == {"signal": WATCHER_PARSE_FAILURE, "path": f"tickets/{stem}/ticket.md",
                              "reason": event.body["reason"]}
        assert isinstance(event.body["reason"], str) and event.body["reason"].strip()
    await rig.drain()
    assert rig.calls == ["other", "old"]
    rig.files.update({"old": text("P0"), "new-invalid": text("P1")})
    await rig.publish("old", "new-invalid")
    assert rig.core.watcher.cache["old"] is not old
    del rig.files["old"]
    await rig.publish("old")
    assert "old" not in rig.core.watcher.cache and "old" not in rig.core.scheduler.pending
    await rig.drain()
    assert rig.calls == ["other", "old", "new-invalid"] and rig.journal.read() == events


@pytest.mark.asyncio
async def test_production_core_preserves_eligibility_order_and_backpressure(tmp_path):
    started, release = asyncio.Event(), asyncio.Event()

    async def prepare(local):
        async def callback(ticket):
            rig.calls.append(ticket.stem)
            if ticket.stem == "pressure-aa":
                started.set()
                await release.wait()
                rig.unmerged = 2
            return "merged"
        return callback

    rig = CoreRig(tmp_path, prepare=prepare)
    for state in ("draft", "rejected", "merged"):
        await rig.add(state, state=state)
    await rig.add("parent", state="merged")
    await rig.add("noop", state="merged")
    child = await rig.add("child", depends="- parent\n- noop")
    assert child.depends == ("parent", "noop")
    for stem in ("reject-held", "quarantine", "drought", "settled", "retired", "running"):
        await rig.add(stem)
    rig.transition("settled", "already_satisfied")
    rig.transition("retired", "rejected")
    rig.transition("running", "running")
    rig.transition("reject-held", "gate_failed", routed="reject_queue")
    rig.quarantine.add("quarantine")
    rig.drought.add("drought")
    assert await rig.core.scheduler.dispatch_next() is None
    rig.transition("parent", "merged")
    assert await rig.core.scheduler.dispatch_next() is None
    rig.transition("noop", "already_satisfied")
    assert await rig.core.scheduler.dispatch_next() is child
    assert await rig.core.scheduler.dispatch_next() is None
    for actor in ("operator", "machine"):
        rig.journal.append(EventType.SIGNAL,
                           {"signal": "reject_verdict", "verdict": "keep", "actor": actor}, ticket="reject-held")
        assert (await rig.core.scheduler.dispatch_next()).stem == "reject-held"
        if actor == "operator":
            await rig.add("reject-held")
            rig.transition("reject-held", "gate_failed", routed="reject_queue")
            assert await rig.core.scheduler.dispatch_next() is None
    rig.quarantine.clear()
    assert (await rig.core.scheduler.dispatch_next()).stem == "quarantine"
    rig.drought.clear()
    assert (await rig.core.scheduler.dispatch_next()).stem == "drought"
    rig.calls.clear()
    for stem, priority in (("zzz-old", "P2"), ("aaa-new", "P2"), ("aaa-missing", "P2"),
                           ("bbb-missing", "P2"), ("urgent", "P0"), ("low", "P3"),
                           ("mid", "P1"), ("tie-aa", "P2"), ("tie-bb", "P2")):
        await rig.add(stem, priority)
    rig.intake("low")
    rig.intake("zzz-old")
    rig.time.advance(10)
    rig.intake("aaa-new")
    rig.time.advance(10)
    rig.intake("zzz-old")
    rig.intake("tie-bb")
    rig.intake("tie-aa")
    for count in (2, 3):
        rig.unmerged = count
        assert await rig.core.scheduler.dispatch_next() is None
    rig.unmerged = 1
    await rig.drain()
    assert rig.calls == ["urgent", "mid", "zzz-old", "aaa-new", "tie-aa", "tie-bb",
                         "aaa-missing", "bbb-missing", "low"]
    await rig.add("pressure-aa")
    await rig.add("pressure-bb")
    first = asyncio.create_task(rig.core.scheduler.dispatch_next())
    await started.wait()
    waiting = asyncio.create_task(rig.core.scheduler.dispatch_next())
    release.set()
    assert (await first).stem == "pressure-aa"
    assert await waiting is None
    rig.unmerged = 0
    assert (await rig.core.scheduler.dispatch_next()).stem == "pressure-bb"
    assert all(e.type != EventType.CAP_CONSUMED for e in rig.journal.read())


@pytest.mark.asyncio
async def test_production_core_reloads_config_only_after_admission(tmp_path):
    started, release, cleaning, finish = (asyncio.Event() for _ in range(4))
    locals, finished = [], []

    async def prepare(local):
        if locals:
            assert finished == ["first"]
        locals.append(local)

        async def callback(ticket):
            if ticket.stem == "first":
                expected = python_values(local.config)
                try:
                    started.set()
                    await release.wait()
                    assert python_values(local.config) == expected
                finally:
                    cleaning.set()
                    await finish.wait()
                    finished.append(ticket.stem)
            return "merged"
        return callback

    explicit = tmp_path / "explicit.yaml"
    rig = CoreRig(tmp_path, prepare=prepare, config_path=explicit)
    (tmp_path / "config.yaml").write_text("invalid default is never loaded")
    first_ticket, next_ticket = await rig.add("first"), await rig.add("second")
    first = asyncio.create_task(rig.core.admission.dispatch(first_ticket))
    await started.wait()
    waiting = asyncio.create_task(rig.core.admission.dispatch(next_ticket))
    await turn()
    assert len(locals) == 1
    rig.put_config(CONFIG.replace("x-med", "x-edited") + "scheduler: {max_unmerged: 5}\n")
    release.set()
    await cleaning.wait()
    assert len(locals) == 1 and not waiting.done()
    finish.set()
    assert await asyncio.gather(first, waiting) == ["merged", "merged"]
    before, after = [local.config for local in locals]
    assert before is not after
    assert (before.scheduler.max_unmerged, after.scheduler.max_unmerged) == (2, 5)
    assert (before.providers[1].models_by_tier.medium, after.providers[1].models_by_tier.medium) == ("x-med", "x-edited")
    rig.put_config("bad: [")
    with pytest.raises(ConfigError):
        await rig.core.admission.dispatch(next_ticket)
    assert len(locals) == 2
    assert_idle(rig.core.admission)
    rig.put_config(CONFIG)
    assert await rig.core.admission.dispatch(next_ticket) == "merged" and len(locals) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["load", "bind", "callback", "cancel"])
async def test_production_core_unwinds_errors_and_cancellation(tmp_path, monkeypatch, failure):
    started, cleaning, release = (asyncio.Event() for _ in range(3))
    calls, prepared = [], []
    error = ValueError("original failure")
    failing = True

    async def prepare(local):
        prepared.append(local)

        async def callback(ticket):
            calls.append(ticket)
            if failing and failure == "callback":
                try:
                    raise error
                finally:
                    cleaning.set()
                    await release.wait()
            if failing and failure == "cancel":
                try:
                    started.set()
                    await asyncio.Event().wait()
                finally:
                    cleaning.set()
                    await release.wait()
            return "merged"
        return callback

    rig = CoreRig(tmp_path, prepare=prepare)
    first_ticket, second_ticket = await rig.add("first"), await rig.add("second")
    original_load, original_replace = cli.load_config, cli.replace

    def load(*args, **kwargs):
        if failing and failure == "load":
            raise error
        return original_load(*args, **kwargs)

    def bind(*args, **kwargs):
        if failing and failure == "bind":
            raise error
        return original_replace(*args, **kwargs)

    monkeypatch.setattr(cli, "load_config", load)
    monkeypatch.setattr(cli, "replace", bind)
    if failure == "cancel":
        first = asyncio.create_task(rig.core.scheduler.dispatch_next())
        await started.wait()
        owned = rig.core.admission.task
        waiter = asyncio.create_task(rig.core.scheduler.dispatch_next())
        await turn()
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        assert calls == [first_ticket] and len(prepared) == 1
        assert not owned.cancelling()
        first.cancel()
        await cleaning.wait()
        second = asyncio.create_task(rig.core.scheduler.dispatch_next())
        await turn()
        assert rig.core.scheduler.active is rig.core.admission.active is first_ticket
        assert rig.core.admission.task is owned and not second.done()
        failing = False
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await first
        assert owned.done() and owned.cancelled() and owned not in asyncio.all_tasks()
        assert await second is second_ticket
    elif failure == "callback":
        first = asyncio.create_task(rig.core.scheduler.dispatch_next())
        await cleaning.wait()
        owned = rig.core.admission.task
        second = asyncio.create_task(rig.core.scheduler.dispatch_next())
        await turn()
        assert calls == [first_ticket] and len(prepared) == 1 and not second.done()
        assert rig.core.scheduler.active is rig.core.admission.active is first_ticket
        assert rig.core.admission.task is owned and not owned.done()
        failing = False
        release.set()
        with pytest.raises(ValueError) as caught:
            await first
        assert caught.value is error and owned.done()
        assert await second is second_ticket
    else:
        with pytest.raises(ValueError) as caught:
            await rig.core.scheduler.dispatch_next()
        assert caught.value is error
        assert_idle(rig.core.admission)
        assert rig.core.scheduler.active is None
        assert prepared == []
        failing = False
        assert await rig.core.scheduler.dispatch_next() is second_ticket
    assert_idle(rig.core.admission)
    assert rig.core.scheduler.active is None and calls[-1] is second_ticket


def observe_preparation(monkeypatch):
    trace, snapshots, contexts = [], [], []
    capture = daemon.snapshot_config
    construct = ProviderLLM.__init__
    preflight = ProviderLLM.preflight
    bind = runner.bind
    from_config = Driver.from_config
    redact = Redactor.from_config
    severity = driver.merge_severity

    def snapshot(config):
        value = capture(config)
        snapshots.append(value)
        trace.append("capture")
        return value

    def provider(self, config, **kwargs):
        assert config is snapshots[-1]
        trace.append("provider")
        construct(self, config, **kwargs)

    async def probe(self):
        assert self._config is snapshots[-1]
        trace.append("preflight-start")
        result = await preflight(self)
        trace.append("preflight-end")
        return result

    def binding(checkout, llm):
        assert trace[-1] == "preflight-end"
        assert checkout.config is llm._config is snapshots[-1]
        trace.append("bind")
        return bind(checkout, llm)

    def driving(cls, config, **kwargs):
        assert config is snapshots[-1]
        trace.append("driver")
        return from_config(config, **kwargs)

    def redacting(cls, config, env):
        assert config is snapshots[-1]
        trace.append("redactor")
        return redact(config, env)

    def merging(config):
        assert config is snapshots[-1]
        trace.append("severity")
        return severity(config)

    original_context = runner.StageContext

    def context(**kwargs):
        assert kwargs["config"] is snapshots[-1]
        ctx = original_context(**kwargs)
        contexts.append(ctx)
        trace.append("context")
        return ctx

    compose = runner.compose_pipeline

    def queue(ctx, *, escalate):
        assert trace[-1] == "context" and ctx is contexts[-1]
        value = compose(ctx, escalate=escalate)
        assert value.ctx is ctx and value.escalate is escalate
        trace.append("queue")
        return value

    monkeypatch.setattr(daemon, "snapshot_config", snapshot)
    monkeypatch.setattr(ProviderLLM, "__init__", provider)
    monkeypatch.setattr(ProviderLLM, "preflight", probe)
    monkeypatch.setattr(runner, "bind", binding)
    monkeypatch.setattr(Driver, "from_config", classmethod(driving))
    monkeypatch.setattr(Redactor, "from_config", classmethod(redacting))
    monkeypatch.setattr(driver, "merge_severity", merging)
    monkeypatch.setattr(runner, "StageContext", context)
    monkeypatch.setattr(runner, "compose_pipeline", queue)
    return trace, snapshots, contexts


@pytest.mark.asyncio
async def test_production_core_uses_real_snapshot_pipeline(tmp_path, monkeypatch):
    trace, snapshots, contexts = observe_preparation(monkeypatch)
    rig = CoreRig(tmp_path, config=CONFIG.replace("review: {}", "review: {gate_severity: {scope_fence: soft}}")
                  + "caps: {retry: 2}\n")
    ticket = await rig.add("work")
    assert trace == []
    reads = []
    original_env, original_resolve = providers.child_env, providers.resolve

    def filtered(env, config, serving=None):
        assert config is snapshots[-1]
        if serving is not None:
            assert serving is next(p for p in config.providers if p.name == serving.name)
        reads.append("env")
        return original_env(env, config, serving)

    def routed(config, tier, surface):
        assert config is snapshots[-1]
        reads.append("route")
        return original_resolve(config, tier, surface)

    monkeypatch.setattr(providers, "child_env", filtered)
    monkeypatch.setattr(providers, "resolve", routed)

    class Reply(BaseModel):
        text: str

    called = []

    async def before_host_work(ctx, original):
        called.append(original)
        assert original is ticket and ctx is contexts[0] and isinstance(ctx, StageContext)
        assert rig.core.admission.active is original and rig.core.admission.task is asyncio.current_task()
        snapshot = snapshots[0]
        assert ctx.config is snapshot and isinstance(ctx.driver, Driver)
        llm = ctx.driver.llm
        assert isinstance(llm, ProviderLLM) and llm._config is snapshot
        for p in snapshot.providers:
            adapter = llm._adapters[p.name]
            assert type(adapter) is providers.ADAPTERS[p.name]
            assert adapter.provider is p and adapter._config is snapshot
            assert adapter._exec is ctx.exec_ is rig.exec and adapter._fs is ctx.fs is rig.fs
        assert providers.resolve(snapshot, "medium", "implement").model == "x-med"
        served = providers.resolve(snapshot, "medium", "review")
        assert served.provider is snapshot.providers[0] and served.model == "c-max"
        assert providers.child_env(ENV, snapshot) == {k: v for k, v in ENV.items() if not k.endswith("_KEY")}
        assert ctx.driver.severity["scope_fence"] == "soft" and ctx.driver.retry_cap == 2
        assert caps.remaining(snapshot.caps, (), original.stem, "retry") == 2
        assert caps.spent(snapshot.caps, (), original.stem) is None
        assert caps.next_rung(snapshot, "medium", "low") == {"tier": "high", "effort": "low"}
        rig.exec.reply = json.dumps({"text": ENV["CLAUDE_KEY"] + " " + ENV["CODEX_KEY"]})
        result = await ctx.driver.run(
            LlmStage(surface="review", emits=Reply, gates=[], render=lambda *_: rig.exec.reply),
            None, ticket=original.stem, attempt=0, workspace=tmp_path,
            tier="medium", effort="low", stuck_budget=60,
        )
        assert result.outcome == "ok" and result.cost.provider == "claude" and result.cost.model == "c-max"
        assert result.artifact.text == "[REDACTED:CLAUDE_KEY] [REDACTED:CODEX_KEY]"
        return "original-terminal"

    monkeypatch.setattr(runner, "drive", before_host_work)
    assert await rig.core.scheduler.dispatch(ticket) == "original-terminal"
    assert called == [ticket] and len(snapshots) == len(contexts) == 1
    assert trace[:4] == ["capture", "provider", "redactor", "preflight-start"]
    assert trace[4:] == ["preflight-end", "bind", "driver", "redactor", "severity", "context", "queue"]
    assert set(reads) == {"env", "route"}
    model_calls = [call for call in rig.exec.calls if call[3] is not None]
    assert len(model_calls) == 6  # Five distinct probes, then one read-only driver call.
    for argv, cwd, env, prompt, _ in model_calls:
        serving, other = ("CLAUDE_KEY", "CODEX_KEY") if argv[0] == "claude" else ("CODEX_KEY", "CLAUDE_KEY")
        assert env[serving] == ENV[serving] and other not in env and cwd == tmp_path
        assert "bypassPermissions" not in argv and "--dangerously-bypass-approvals-and-sandbox" not in argv
        assert all(ENV[name] not in prompt for name in (serving, other))
    for data in rig.fs.files.values():
        assert all(ENV[name].encode() not in data for name in ("CLAUDE_KEY", "CODEX_KEY"))
    assert all(ENV[name] not in str(rig.journal.read()) for name in ("CLAUDE_KEY", "CODEX_KEY"))
    assert_idle(rig.core.admission)


@pytest.mark.asyncio
async def test_production_core_awaits_preflight_inside_admission(tmp_path, monkeypatch):
    trace, snapshots, contexts = observe_preparation(monkeypatch)
    rig = CoreRig(tmp_path)
    first_ticket, second_ticket = await rig.add("first"), await rig.add("second")
    started, release = asyncio.Event(), asyncio.Event()
    called = []

    async def hook(argv):
        assert asyncio.current_task() is rig.core.admission.task
        if not started.is_set():
            assert trace == ["capture", "provider", "redactor", "preflight-start"]
            started.set()
            await release.wait()

    async def stop(ctx, ticket):
        assert ctx.config is snapshots[-1] and trace[-1] == "queue"
        called.append(ticket)
        return "merged"

    rig.exec.hook = hook
    monkeypatch.setattr(runner, "drive", stop)
    assert trace == [] and rig.exec.calls == [] and not contexts
    first = asyncio.create_task(rig.core.admission.dispatch(first_ticket))
    await started.wait()
    owned = rig.core.admission.task
    waiter = asyncio.create_task(rig.core.admission.dispatch(second_ticket))
    cancelled = asyncio.create_task(rig.core.admission.dispatch(second_ticket))
    await turn()
    cancelled.cancel()
    with pytest.raises(asyncio.CancelledError):
        await cancelled
    assert len(snapshots) == 1 and not contexts and not called and not waiter.done()
    assert rig.core.admission.task is owned and not owned.cancelling()
    rig.put_config(CONFIG.replace("x-med", "x-edited"))
    release.set()
    assert await asyncio.gather(first, waiter) == ["merged", "merged"]
    assert called == [first_ticket, second_ticket]
    assert len(snapshots) == len(contexts) == 2 and snapshots[0] is not snapshots[1]
    assert [s.providers[1].models_by_tier.medium for s in snapshots] == ["x-med", "x-edited"]
    assert [c.driver.llm._config for c in contexts] == snapshots
    assert contexts[0].driver.llm is not contexts[1].driver.llm
    for step in ("capture", "provider", "preflight-start", "preflight-end", "bind", "driver", "context", "queue"):
        assert trace.count(step) == 2
    probed = [argv[argv.index("-m") + 1] for argv, _, _, prompt, _ in rig.exec.calls
              if argv[0] == "codex" and prompt is not None]
    assert probed == ["x-med", "x-low", "x-edited", "x-low"]
    assert_idle(rig.core.admission)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["refusal", "error", "cancel"])
async def test_production_core_unwinds_preflight_refusal_and_cancellation(tmp_path, monkeypatch, failure):
    trace, snapshots, contexts = observe_preparation(monkeypatch)
    rig = CoreRig(tmp_path)
    first_ticket, second_ticket = await rig.add("first"), await rig.add("second")
    assert trace == []
    started, cleaning, finish = (asyncio.Event() for _ in range(3))
    error = ValueError("version probe failed")
    called = []

    async def hook(argv):
        if failure == "error":
            raise error
        if failure == "cancel":
            try:
                started.set()
                await asyncio.Event().wait()
            finally:
                cleaning.set()
                await finish.wait()

    async def stop(ctx, ticket):
        called.append(ticket)
        return "merged"

    rig.exec.hook = hook
    rig.exec.latest = "9.9.9" if failure == "refusal" else "1.2.3"
    monkeypatch.setattr(runner, "drive", stop)
    if failure == "cancel":
        first = asyncio.create_task(rig.core.admission.dispatch(first_ticket))
        await started.wait()
        owned = rig.core.admission.task
        first.cancel()
        await cleaning.wait()
        second = asyncio.create_task(rig.core.admission.dispatch(second_ticket))
        await turn()
        assert len(snapshots) == 1 and not contexts and not called and not second.done()
        assert rig.core.admission.task is owned and rig.core.admission.active is first_ticket
        rig.exec.hook = None
        finish.set()
        with pytest.raises(asyncio.CancelledError):
            await first
        assert owned.done() and owned.cancelled() and owned not in asyncio.all_tasks()
        assert await second == "merged"
    else:
        with pytest.raises(runner.Refusal if failure == "refusal" else ValueError) as caught:
            await rig.core.admission.dispatch(first_ticket)
        if failure == "refusal":
            message = str(caught.value)
            assert "provider preflight failed" in message and "latest release 9.9.9" in message
            assert "pnpm add -g test-cli@latest" in message
            assert "fix each named provider, then run the same command again" in message
        else:
            assert caught.value is error
        assert not contexts and not called and "bind" not in trace
        assert_idle(rig.core.admission)
        rig.exec.hook, rig.exec.latest = None, "1.2.3"
        assert await rig.core.admission.dispatch(second_ticket) == "merged"
    assert called == [second_ticket] and len(contexts) == 1 and len(snapshots) == 2
    assert trace.count("bind") == trace.count("context") == 1
    assert_idle(rig.core.admission)


@pytest.mark.parametrize("refuse", [False, True])
def test_bootstrap_pipeline_prepares_before_dispatch(tmp_path, monkeypatch, refuse):
    rig = CoreRig(tmp_path)
    ticket = asyncio.run(rig.add("work"))
    bound, called = [], []
    original_bind = runner.bind

    def bind(checkout, llm):
        assert checkout is rig.checkout and llm._config is checkout.config
        assert len([call for call in rig.exec.calls if call[3] is not None]) == 5
        bound.append(checkout)
        return original_bind(checkout, llm)

    async def stop(ctx, original):
        assert original is ticket and ctx.config is rig.checkout.config
        called.append(original)
        return "merged"

    monkeypatch.setattr(runner, "bind", bind)
    monkeypatch.setattr(runner, "drive", stop)
    rig.exec.latest = "9.9.9" if refuse else "1.2.3"
    if refuse:
        with pytest.raises(runner.Refusal, match="provider preflight failed"):
            runner.pipeline(rig.checkout)
        assert bound == called == []
    else:
        callback = runner.pipeline(rig.checkout)
        assert bound == [rig.checkout] and called == []
        assert asyncio.run(callback(ticket)) == "merged" and called == [ticket]
    assert_idle(rig.core.admission)


def capture_pipeline_queue(monkeypatch):
    captured = []
    compose = runner.compose_pipeline

    def recording(ctx, *, escalate):
        queue = compose(ctx, escalate=escalate)
        captured.append((ctx, escalate, queue))
        return queue

    monkeypatch.setattr(runner, "compose_pipeline", recording)
    return captured


@pytest.mark.asyncio
async def test_production_pipeline_composes_merge_queue(tmp_path, monkeypatch):
    captured = capture_pipeline_queue(monkeypatch)
    rig = CoreRig(tmp_path)
    assert captured == []
    callback = runner.bind(rig.checkout, FakeLLM([]))
    [(ctx, consumer, queue)] = captured
    assert isinstance(queue, MergeQueue) and queue.ctx is ctx and queue.escalate is consumer
    for field in ("repo", "config", "env", "exec_", "git", "fs"):
        assert getattr(ctx, field) is getattr(rig.checkout, field)
    assert ctx.driver.clock is rig.checkout.clock and ctx.driver.sleep is rig.checkout.sleep
    assert ctx.driver.effects._journal is ctx.driver.journal
    assert ctx.driver.spool._fs is ctx.fs
    assert queue.pending == {} and queue.active is None and not queue.paused and queue.red_stems == []
    seen = []

    async def dispatch(context, ticket):
        assert context is ctx
        seen.append(ticket)
        return "merged"

    monkeypatch.setattr(runner, "drive", dispatch)
    ticket = await rig.add("work")
    assert await callback(ticket) == "merged" and seen == [ticket]
    event = rig.journal.append(EventType.SIGNAL, {"kind": "merge_red_streak", "stems": ["work"], "limit": 3},
                               ticket="work")
    before = ctx.driver.journal.read()
    assert consumer(event) is None
    assert ctx.driver.journal.read() == before and rig.exec.calls == [] and rig.fs.files == {}
    recorded = []
    supplied = recorded.append
    direct = merge.compose_pipeline(ctx, escalate=supplied)
    assert direct.ctx is ctx and direct.escalate is supplied
    direct.escalate(event)
    assert recorded == [event] and ctx.driver.journal.read() == before
    with pytest.raises(TypeError):
        merge.compose_pipeline(ctx)


@pytest.mark.asyncio
async def test_merge_queue_composition_has_no_side_effects(tmp_path, monkeypatch):
    rig = CoreRig(tmp_path)
    captured = capture_pipeline_queue(monkeypatch)

    def forbidden(*args, **kwargs):
        pytest.fail("composition performed admission or an external effect")

    for owner, names in ((MergeQueue, ("offer", "process", "_signal")),
                         (Git, ("_call",)), (stages, ("gather_evidence", "gather_safety_evidence")),
                         (Journal, ("append",)), (asyncio, ("create_task",)),
                         (rig.exec, ("run",)), (rig.fs, ("write", "replace"))):
        for name in names:
            monkeypatch.setattr(owner, name, forbidden)
    tasks = asyncio.all_tasks()
    callback = runner.bind(rig.checkout, FakeLLM([]))
    [(ctx, _, queue)] = captured
    assert callable(callback) and queue.ctx is ctx
    direct = merge.compose_pipeline(ctx, escalate=forbidden)
    assert direct.ctx is ctx
    assert asyncio.all_tasks() == tasks and rig.journal.read() == []
    assert rig.exec.calls == [] and rig.fs.files == {}


@pytest.mark.asyncio
async def test_composed_merge_queue_admits_reviewed_candidate(admission_context, monkeypatch):
    source = admission_context
    checkout = runner.Checkout(source.repo, source.config, source.env, source.exec_, source.git,
                               source.driver.journal, source.fs, source.driver.clock, source.driver.sleep)
    captured = capture_pipeline_queue(monkeypatch)
    callback = runner.bind(checkout, FakeLLM([]))
    [(ctx, consumer, queue)] = captured
    assert callable(callback) and queue.ctx is ctx and queue.escalate is consumer
    ticket = await ready(ctx, verification=(("grep", "-q", "ok", "chupa/thing.py"),))
    reviewed = await ctx.git.rev_parse(ctx.repo, ticket.stem)
    queue.offer(ticket, attempt=7)
    assert queue.pending == {ticket.stem: (ticket, 7)}
    [result] = await queue.process()
    assert result.outcome == "ok", result.findings
    artifact = result.artifact
    assert isinstance(artifact, merge.Admission)
    assert artifact.stem == ticket.stem and artifact.reviewed_sha == reviewed
    assert artifact.commit == await ctx.git.rev_parse(ctx.repo, "main")
    assert artifact.produced_at_sha == artifact.commit and artifact.produced_by_spec_version == merge.MERGE_SPEC_VERSION
    events = ctx.driver.journal.read()
    [merged] = [e for e in events if e.type == EventType.STATE_TRANSITION]
    assert merged.ticket == ticket.stem and merged.key is None
    assert merged.body == {"to": "merged", "commit": artifact.commit, "reviewed_sha": reviewed}
    [completion] = [e for e in events if e.type == EventType.EFFECT_COMPLETION]
    assert completion.key == f"merge/{ticket.stem}/7"
    [facts] = [e for e in events if e.type == EventType.SIGNAL]
    assert facts.ticket == ticket.stem and facts.key is None
    assert facts.body == {"kind": CONFLICT_FACTS, "conflicted_paths": [], "resolving_rung": "none",
                          "strategy_paths": [], "integration_red_paths": []}
    assert (ctx.config.state_dir / "spools" / ticket.stem / "7/merge-integration/verify-01.txt").is_file()
    assert not ctx.worktree(ticket.stem).exists()
    assert await ctx.git._run(ctx.repo, "branch", "--list", ticket.stem) == ""
    assert queue.pending == {} and queue.active is None


def sources():
    root = Path(__file__).resolve().parents[1]
    material = {".".join(p.relative_to(root).with_suffix("").parts): p.read_text()
                for p in (root / "chupa").rglob("*.py")}
    material["chupa"] = material.pop("chupa.__init__")
    return material


def without_core_import(material):
    edge = "from chupa.daemon import DaemonCore, daemon_core"
    assert edge in material["chupa.__main__"]
    return {name: "\n".join(line[:len(line) - len(line.lstrip())] + "pass"
            if line.lstrip().startswith("from chupa.daemon import") else line
            for line in source.splitlines()) for name, source in material.items()}


def assert_reachable(material):
    assert {"chupa.daemon", "chupa.scheduler", "chupa.watcher"} <= import_closure(material)


def test_daemon_core_is_reachable_from_cli():
    material = sources()
    assert_reachable(material)
    removed = without_core_import(material)
    with pytest.raises(AssertionError):
        assert_reachable(removed)
    for edge in ("import chupa.daemon", "from chupa import daemon"):
        restored = {**removed, "chupa.status": removed["chupa.status"] + "\n" + edge}
        assert_reachable(restored)


def production_writer(source, script):
    """Reuse the production bind and its queue with the disposable admission repository."""
    checkout = runner.Checkout(source.repo, source.config, source.env, source.exec_, source.git,
                               source.driver.journal, source.fs, source.driver.clock, source.driver.sleep)
    writer = runner.bind(checkout, FakeLLM(script))
    return checkout, writer


@pytest.mark.asyncio
async def test_production_composes_rework_without_running_it(tmp_path, monkeypatch):
    rig = CoreRig(tmp_path)
    def forbidden(*args, **kwargs):
        pytest.fail("Rework composition performed work")
    for owner, names in ((daemon, ("rework", "apply_rework")), (Git, ("_call",)),
                         (Journal, ("append",)), (asyncio, ("create_task",)),
                         (rig.fs, ("write", "replace"))):
        for name in names:
            monkeypatch.setattr(owner, name, forbidden)
    before = asyncio.all_tasks()
    writer = runner.bind(rig.checkout, FakeLLM([]))
    assert isinstance(writer, daemon.TicketWriter) and writer.queue.ctx is writer.ctx
    assert writer.ctx.driver.journal is rig.checkout.journal
    assert writer.ctx.driver.effects._journal is rig.checkout.journal
    assert writer.ctx.fs is rig.checkout.fs and writer.ctx.git is rig.checkout.git
    assert writer.ctx.driver.clock is rig.checkout.clock and writer.ctx.driver.sleep is rig.checkout.sleep
    assert before == asyncio.all_tasks() and rig.journal.read() == []
    assert rig.fs.files == {} and rig.exec.calls == []


@pytest.mark.asyncio
async def test_production_consumes_conflict_handoff_after_unwind(admission_context, monkeypatch):
    from chupa.mergequeue import ConflictHandoff
    from tests.test_mergequeue import conflict
    from tests.test_stages import agent, verdict
    from tests.test_rework import order, requisition
    source = admission_context
    _, writer = production_writer(source, [])
    ctx, queue = writer.ctx, writer.queue
    ticket, path = await conflict(ctx)
    ctx.config.merge.strategies = []
    text = (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text()
    chronology = []
    call = ctx.git._call
    async def observe(root, *args, **kwargs):
        value = await call(root, *args, **kwargs)
        if args == ("rebase", "--abort"):
            chronology.append("abort")
        return value
    monkeypatch.setattr(ctx.git, "_call", observe)
    def forbid(*args, **kwargs):
        pytest.fail("handoff reused code approval or called diagnosis")
    monkeypatch.setattr(runner, "diagnose", forbid)
    monkeypatch.setattr(ctx.git, "merge_squash", forbid)
    queue.offer(ticket, attempt=0)
    [handoff] = await queue.process()
    assert isinstance(handoff, ConflictHandoff) and handoff.approval_invalidated
    assert chronology == ["abort"] and not ctx.driver.llm.requests
    assert queue.active is None and not queue._slot.locked()
    def reply(req):
        assert queue.active is None and not queue._slot.locked()
        chronology.append("rework")
        assert handoff.model_dump_json() in req.rendered
        assert path in req.rendered and all(f.message in req.rendered for f in handoff.findings)
        assert text in req.rendered
        return order("update", [(ticket.stem, text.replace("holds the word ok", "holds the word ok after fresh review"))])
    ctx.driver.llm = FakeLLM([reply, requisition()])
    from chupa.drain import _Drain
    from chupa.lockfile import Lockfile, LockHeld
    checkout = runner.Checkout(ctx.repo, ctx.config, ctx.env, ctx.exec_, ctx.git,
                               ctx.driver.journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
    lock = Lockfile(ctx.config.state_dir, instance_id="production", clock=ctx.driver.clock)
    lock.acquire()
    try:
        async def consume(original):
            contender = Lockfile(ctx.config.state_dir, instance_id="contender", clock=ctx.driver.clock)
            with pytest.raises(LockHeld):
                contender.acquire()
            return await writer.consume_handoff(original, handoff, attempt=0)
        await _Drain(checkout, consume, frozenset())._run_one(ticket, False, "blob")
    finally:
        lock.release()
    assert chronology == ["abort", "rework"]
    events = ctx.driver.journal.read()
    [terminal] = [e.body for e in events if e.type == EventType.STATE_TRANSITION and e.body.get("to") != "running"]
    assert terminal == {"to": "gate_failed", "stage": "merge",
                        "reason": ",".join(sorted({f.code for f in handoff.findings})), "dispatch": "retry"}
    assert not any(e.type == EventType.CAP_CONSUMED for e in events)
    assert [r.surface for r in ctx.driver.llm.requests] == ["rework", "requisition_review"]
    assert not ctx.worktree(ticket.stem).exists()
    # Re-offer uses the ordinary Implement/Check/Review path, never the invalidated queue approval.
    monkeypatch.undo()
    ctx.driver.llm = FakeLLM([agent({"chupa/thing.py": "ok fresh\n"}),
                             verdict()])
    fresh = stages.validate_ticket(ticket.stem, (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text(), ctx.repo)
    await writer(fresh)
    assert [r.surface for r in ctx.driver.llm.requests] == ["implement", "review"]


@pytest.mark.asyncio
@pytest.mark.parametrize("action", ["update", "split", "escalate", "exhausted"])
async def test_production_applies_reviewed_rework_orders(admission_context, action):
    from chupa.mergequeue import ConflictHandoff
    from chupa.rework import SUPERSEDES, record_supersedes
    from tests.test_rework import order, requisition, successors
    checkout, writer = production_writer(admission_context, [])
    ctx = writer.ctx
    ticket = await ready(ctx)
    text = (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text()
    if action == "exhausted":
        from tests.test_mergequeue import commit
        text = text.replace("kind: feature", "kind: feature\nagent_tier: max\nagent_effort: max")
        ctx.fs.write(ctx.repo / f"tickets/{ticket.stem}/ticket.md", text.encode())
        await commit(ctx, ctx.repo, [f"tickets/{ticket.stem}/ticket.md"])
        ticket = stages.validate_ticket(ticket.stem, text, ctx.repo)
    proposals = successors(text.strip()) if action == "split" else [(ticket.stem, text.strip().replace("holds the word ok", "holds ok after narrowing"))] if action == "update" else []
    ctx.driver.llm = FakeLLM([order("escalate" if action == "exhausted" else action, proposals)]
                            + [requisition() for _ in proposals])
    finding = stages.Finding(code="post_rebase_regate", message="conflict", paved_road="fresh review")
    handoff = ConflictHandoff(stem=ticket.stem, reviewed_sha=await ctx.git.rev_parse(ctx.repo, ticket.stem),
                              conflicted_paths=["chupa/thing.py"], findings=[finding, finding])
    from chupa.drain import _Drain
    from chupa.lockfile import Lockfile
    returned = []
    async def consume(original):
        result = await writer.consume_handoff(original, handoff, attempt=0)
        returned.append(result)
        return result
    lock = Lockfile(ctx.config.state_dir, instance_id="production", clock=ctx.driver.clock)
    lock.acquire()
    try:
        await _Drain(checkout, consume, frozenset())._run_one(
            ticket, False, await ctx.git.rev_parse(ctx.repo, f"HEAD:tickets/{ticket.stem}/ticket.md"))
    finally:
        lock.release()
    [result] = returned
    events = ctx.driver.journal.read()
    transitions = [e for e in events if e.type == EventType.STATE_TRANSITION and e.body.get("to") != "running"]
    terminal = transitions[0].body
    assert {k: terminal[k] for k in ("to", "stage", "reason")} == {
        "to": "gate_failed", "stage": "merge", "reason": "post_rebase_regate"}
    maps = [e for e in events if e.body.get("signal") == SUPERSEDES]
    if action == "split":
        assert result == "rejected" and transitions[-1].body == {"to": "rejected"}
        assert terminal == {"to": "gate_failed", "stage": "merge", "reason": "post_rebase_regate"}
        [mapping] = maps
        assert events.index(mapping) < events.index(transitions[0]) < events.index(transitions[-1])
        for stem, proposal in proposals:
            assert await ctx.git._run(ctx.repo, "show", f"HEAD:tickets/{stem}/ticket.md") == proposal
        assert "state: rejected" in (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text()
        from chupa.rework import ReworkOrder
        replay = ReworkOrder(action="split", tickets=[{"stem": s, "ticket": t} for s, t in proposals],
                             stem=ticket.stem, attempt=0, produced_by_spec_version=1, produced_at_sha="reviewed")
        count = len(events)
        assert await record_supersedes(ctx, replay) == [] and len(ctx.driver.journal.read()) == count
    else:
        assert result == "gate_failed" and maps == [] and len(transitions) == 1
        if action == "update":
            assert terminal["dispatch"] == "retry" and "routed" not in terminal and "rung" not in terminal
            assert await ctx.git._run(ctx.repo, "show", f"HEAD:tickets/{ticket.stem}/ticket.md") == proposals[0][1]
        elif action == "escalate":
            assert terminal["dispatch"] == "escalate" and "rung" in terminal and "routed" not in terminal
        else:
            assert terminal["dispatch"] == terminal["routed"] == "reject_queue" and "rung" not in terminal
        if action != "update":
            assert (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text() == text
    assert not any(e.type == EventType.CAP_CONSUMED for e in events)
    assert not ctx.worktree(ticket.stem).exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("action", ["split", "update"])
@pytest.mark.parametrize("failure", ["validation", "review", "write", "add", "commit", "partial", "incomplete", "all-commits", "spent"])
async def test_production_refuses_failed_rework_publication(admission_context, monkeypatch, failure, action):
    from chupa.mergequeue import ConflictHandoff
    from tests.test_rework import order, requisition, successors
    checkout, writer = production_writer(admission_context, [])
    ctx = writer.ctx
    ticket = await ready(ctx)
    text = (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text()
    proposals = (successors(text) if action == "split" else
                 [(ticket.stem, text.replace("holds the word ok", "holds ok after narrowing"))])
    ctx.driver.retry_cap = 0
    script = [order(action, proposals), *[requisition() for _ in proposals]]
    if failure == "validation":
        script = [order("update", [(ticket.stem, "invalid ticket")])]
    if failure == "review":
        script = [order(action, proposals), requisition("rma")]
    if failure == "write":
        write = ctx.fs.write
        def failed_write(path, data):
            if path == ctx.repo / f"tickets/{proposals[-1][0]}/ticket.md":
                raise RuntimeError("proposal write failed")
            write(path, data)
        monkeypatch.setattr(ctx.fs, "write", failed_write)
    if failure == "add":
        add = ctx.git.add
        failed_once = False
        async def failed_add(root, paths):
            nonlocal failed_once
            if root == ctx.repo and paths == [f"tickets/{s}/ticket.md" for s, _ in proposals] and not failed_once:
                failed_once = True
                raise RuntimeError("proposal add failed")
            await add(root, paths)
        monkeypatch.setattr(ctx.git, "add", failed_add)
    if failure in {"commit", "partial", "incomplete", "all-commits"}:
        commit = ctx.git.commit
        async def failed(root, message, **kwargs):
            if message.endswith(": rework") or failure == "all-commits":
                if failure in {"partial", "incomplete"}:
                    await commit(root, message, only=[f"tickets/{proposals[0][0]}/ticket.md"])
                    if failure == "incomplete" and action == "split":
                        return
                raise RuntimeError("publication failed")
            await commit(root, message, **kwargs)
        monkeypatch.setattr(ctx.git, "commit", failed)
    if failure == "spent":
        for _ in range(ctx.config.caps.retry):
            caps.consume(ctx.driver.journal, ticket.stem, "retry", "old")
        script = []
    ctx.driver.llm = FakeLLM(script)
    handoff = ConflictHandoff(stem=ticket.stem, reviewed_sha="reviewed", conflicted_paths=[],
                              findings=[stages.Finding(code="post_rebase_regate", message="conflict", paved_road="fresh review")])
    assert await writer.consume_handoff(ticket, handoff, attempt=0) == "gate_failed"
    events = ctx.driver.journal.read()
    [terminal] = [e.body for e in events if e.type == EventType.STATE_TRANSITION]
    assert terminal == {"to": "gate_failed", "stage": "merge", "reason": "post_rebase_regate",
                        "dispatch": "reject_queue", "routed": "reject_queue"}
    assert not any(e.body.get("signal") == "supersedes" for e in events)
    assert (ctx.repo / f"tickets/{ticket.stem}/ticket.md").read_text() == text
    assert await ctx.git._run(ctx.repo, "show", f"HEAD:tickets/{ticket.stem}/ticket.md") == text
    assert not (ctx.repo / "tickets/piece-one/ticket.md").exists()
    assert not (ctx.repo / "tickets/piece-two/ticket.md").exists()
    assert caps.draws(events, ticket.stem, "diagnosis") == 0
    assert caps.draws(events, ticket.stem, "retry") == (ctx.config.caps.retry if failure == "spent" else 0)
    if failure == "spent":
        assert ctx.driver.llm.requests == []
    else:
        artifact = json.loads((ctx.repo / f"tickets/{ticket.stem}/attempts/0/harvest.json").read_text())
        assert len(artifact["findings"]) >= 2 and all(f["paved_road"] for f in artifact["findings"])
    if failure != "all-commits":
        assert await ctx.git.status_porcelain(ctx.repo) == ""
        # A later ordinary drain must not intake a leaked machine proposal as human work.
        from chupa.drain import drain
        from tests.test_drain_reentry import NoChild
        intake_before = [e for e in events if e.body.get("signal") == INTAKE_SIGNAL]
        for _ in range(ctx.config.caps.retry - caps.draws(events, ticket.stem, "retry")):
            caps.consume(ctx.driver.journal, ticket.stem, "retry", "old")
        async def forbidden(ticket):
            pytest.fail("following drain dispatched refused Rework output")
        await drain(checkout, forbidden, reexec=NoChild())
        assert [e for e in ctx.driver.journal.read() if e.body.get("signal") == INTAKE_SIGNAL] == intake_before
        assert await ctx.git.status_porcelain(ctx.repo) == ""
