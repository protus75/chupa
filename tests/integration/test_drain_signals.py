import asyncio
import json

from chupa import __main__ as cli
from chupa import runner
from chupa.llm import FakeLLM
from tests.integration.test_cli import ENV
from tests.integration.test_drain import Clock, commit_ticket, confirmed, journal, root
from tests.integration.test_stages import agent


def test_signal_kills_a_running_drain_like_kill(root, monkeypatch, capsys):
    commit_ticket(root, "work", confirmed())
    callbacks, restored, life = [], [], []

    def signals(callback):
        callbacks.append(callback)
        return lambda: restored.append(True)

    monkeypatch.setattr(cli, "_engine_signals", signals)

    class Blocking(FakeLLM):
        async def call(self, req):
            callbacks[0]()
            await asyncio.Event().wait()

    def pipeline(checkout):
        life.append(checkout.control.inbox.lifecycle_id)
        return runner.bind(checkout, Blocking([agent({}, outcome="already_satisfied")]))

    assert cli.main(["drain"], cwd=root, env=ENV, clock=Clock(), pipeline=pipeline) == runner.EXIT_TICKET
    assert "drain stopped by kill -- NOT quiescent" in capsys.readouterr().out
    events = [json.loads(line) for line in (root / ".chupa/state/engine.log").read_text().splitlines()]
    assert any(e["event"] == "engine_stop" and e["verb"] == "drain" and e["outcome"] == "killed" for e in events)
    assert any(
        e.body.get("kind") == "control_decision" and e.body.get("verb") == "kill" and e.body.get("decision") == "accepted" and e.body.get("lifecycle_id") == life[0] for e in journal(root).read()
    )
    assert restored == [True]
