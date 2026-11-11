import asyncio
import json
import signal
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from chupa import __main__ as cli
from chupa.drain import _Drain


def test_engine_signals_covers_hangup(monkeypatch):
    async def exercise():
        loop = asyncio.get_running_loop()
        added, removed = {}, []
        monkeypatch.setattr(loop, "add_signal_handler", lambda sig, cb: added.__setitem__(sig, cb))
        monkeypatch.setattr(loop, "remove_signal_handler", removed.append)

        def callback():
            pass

        restore = cli._engine_signals(callback)
        expected = {signal.SIGINT, signal.SIGTERM, signal.SIGHUP}
        assert set(added) == expected
        assert all(cb is callback for cb in added.values())
        restore()
        assert set(removed) == expected and len(removed) == 3

    asyncio.run(exercise())


def test_signal_kill_publishes_a_kill_request():
    published = []
    checkout = SimpleNamespace(
        clock=lambda: datetime(2026, 1, 1, tzinfo=UTC),
        config=SimpleNamespace(state_dir=Path("/state"), drain=SimpleNamespace(max_runtime_hours=2)),
        control=SimpleNamespace(inbox=SimpleNamespace(lifecycle_id="life-1")),
        fs=SimpleNamespace(publish=lambda path, data: published.append((path, data))),
    )
    run = _Drain(checkout, None, frozenset())
    run._signal_kill()
    [(path, data)] = published
    assert path.parent == Path("/state/control/inbox")
    value = json.loads(data)
    assert value["verb"] == "kill" and value["lifecycle_id"] == "life-1" and value["hold_id"] is None
    assert path.name == value["request_id"] + ".json"
