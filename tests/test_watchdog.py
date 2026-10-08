import asyncio
import json

import pytest
from pydantic import BaseModel

from chupa import runner
from chupa.driver import LlmStage
from chupa.providers import CliAdapter, ProviderLLM
from chupa.watchdog import EventConsumer
from tests.test_daemon_composition import CoreRig
from tests.test_providers import (PythonProviderExec, claude_ok, codex_ok, config, jsonl,
                                 provider_request, python_client)


def tool_events(name):
    if name == "claude":
        block = {"type": "tool_use", "id": "tool-1", "name": "Read", "input": {"file_path": "a.py"}}
        return [{"type": "assistant", "message": {"id": "msg-1", "content": [block]}},
                {"type": "assistant", "message": {"id": "msg-1", "content": [block]}}]
    item = {"id": "tool-1", "type": "command_execution", "command": "cat a.py"}
    return [{"type": kind, "item": {**item, "status": status}}
            for kind, status in (("item.started", "in_progress"), ("item.updated", "in_progress"),
                                 ("item.completed", "completed"))]


@pytest.mark.parametrize("name", ["claude", "codex"])
def test_event_consumer_receives_before_terminal(tmp_path, name):
    cfg = config(tmp_path)

    async def scenario():
        connection = asyncio.get_running_loop().create_future()

        def connected(reader, writer):
            connection.set_result((reader, writer))

        server = await asyncio.start_server(connected, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        first, second = tool_events(name)[:2]
        terminal = (claude_ok if name == "claude" else codex_ok)()
        # Hold first after an incomplete line, then after two complete tool events.
        line = jsonl(first).encode()
        script = (
            "import os, socket\n"
            f"os.write(1, {line[:8]!r})\n"
            f"gate = socket.create_connection(('127.0.0.1', {port}))\n"
            "gate.recv(1)\n"
            f"os.write(1, {line[8:] + jsonl(second).encode()!r})\n"
            "gate.recv(1)\n"
            f"os.write(1, {terminal.encode()!r})\n"
        )
        process = PythonProviderExec(script)
        client = python_client(cfg, process, tmp_path)
        events, delivered = [], asyncio.Event()

        def consume(event):
            events.append(event)
            if len(events) == 2:
                delivered.set()

        task = asyncio.create_task(client.call(provider_request(name, tmp_path), consumer=EventConsumer(consume)))
        writer = None
        try:
            _, writer = await asyncio.wait_for(connection, 5)
            assert events == [] and not task.done()
            writer.write(b"1")
            await writer.drain()
            await asyncio.wait_for(delivered.wait(), 5)
            assert events == [first, second] and not task.done()
            assert list((cfg.state_dir / "spools").rglob("events.jsonl")) == []
            writer.write(b"2")
            await writer.drain()
            result = await asyncio.wait_for(task, 5)
            assert result.text == ("done" if name == "claude" else "patched")
            assert events == [first, second, *[json.loads(line) for line in terminal.splitlines()]]
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            if writer is not None:
                writer.close()
                await writer.wait_closed()
            server.close()
            await server.wait_closed()

    asyncio.run(scenario())


@pytest.mark.parametrize("name", ["claude", "codex"])
@pytest.mark.parametrize("with_usage", [True, False])
def test_event_consumer_preserves_tool_identity_and_optional_usage(tmp_path, name, with_usage):
    tools = tool_events(name)
    if name == "claude":
        terminal = {"type": "result", "subtype": "success", "is_error": False,
                    "result": "done", "total_cost_usd": 0.42}
        if with_usage:
            terminal["usage"] = {"input_tokens": 10, "output_tokens": 7}
        expected = [*tools, terminal]
    else:
        terminal = {"type": "turn.completed"}
        if with_usage:
            terminal["usage"] = {"input_tokens": 10, "output_tokens": 7}
        expected = [*tools, {"type": "item.completed", "item": {
            "id": "message-1", "type": "agent_message", "text": "done"}}, terminal]
    script = f"import os; os.write(1, {jsonl(*expected).encode()!r})"
    client = python_client(config(tmp_path), PythonProviderExec(script), tmp_path)
    events = []
    result = asyncio.run(client.call(provider_request(name, tmp_path), consumer=EventConsumer(events.append)))
    assert events == expected
    ids = ([event["message"]["content"][0]["id"] for event in events[:len(tools)]] if name == "claude"
           else [event["item"]["id"] for event in events[:len(tools)]])
    assert ids == ["tool-1"] * len(tools)
    assert ("usage" in events[-1]) is with_usage
    assert (result.input_tokens, result.output_tokens) == ((10, 7) if with_usage else (None, None))
    assert result.usd == (0.42 if name == "claude" else 1.5)
    assert not list(tmp_path.rglob("journal"))


@pytest.mark.asyncio
async def test_event_stream_is_dormant(tmp_path, monkeypatch):
    rig = CoreRig(tmp_path)
    rig.exec.reply = '{"text": "done"}'
    calls = []
    invoke = CliAdapter.invoke

    async def observe(self, req, model, **kwargs):
        assert kwargs.get("consumer") is None
        calls.append((self.provider.name, req.surface))
        return await invoke(self, req, model, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError("production constructed an event consumer")

    monkeypatch.setattr(CliAdapter, "invoke", observe)
    monkeypatch.setattr(EventConsumer, "__init__", forbidden)

    class Reply(BaseModel):
        text: str

    async def drive(ctx, ticket):
        assert isinstance(ctx.driver.llm, ProviderLLM)
        for surface in ("implement", "review"):
            result = await ctx.driver.run(
                LlmStage(surface=surface, emits=Reply, gates=[], render=lambda *_: "probe"), None,
                ticket=ticket.stem, attempt=0, workspace=tmp_path, tier="medium", effort="low", stuck_budget=600,
            )
            assert result.outcome == "ok" and result.artifact.text == "done"
        return "merged"

    monkeypatch.setattr(runner, "drive", drive)
    await rig.add("ordinary")
    await rig.drain()
    assert ("codex", "implement") in calls and ("claude", "review") in calls
    assert not any("spiral" in str(event.body) for event in rig.journal.read())

    call = ProviderLLM.call

    async def activated(self, req):
        return await call(self, req, consumer=EventConsumer(lambda event: None))

    monkeypatch.setattr(ProviderLLM, "call", activated)
    await rig.add("activated")
    with pytest.raises(AssertionError):
        await rig.drain()  # The same production graph must fail once consumer construction is wired.
