import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa import __main__ as entry
from chupa import runner
from chupa.lockfile import LockHeld


@pytest.mark.parametrize("holder", [{"verb": "drain"}, {"verb": "serve"}, {"verb": "triage"}, {"verb": "eval"}, {}, None])
@pytest.mark.parametrize("route", ["control", "verdict", "retro"])
def test_held_lock_routes_only_to_engine(monkeypatch, holder, route):
    class FakePath:
        def __truediv__(self, other):
            return self

        def is_file(self):
            return False

    class FakeLock:
        def __init__(self, *args, **kwargs):
            pass

        def acquire(self):
            raise LockHeld(Path("lock"), holder)

    async def describe(repo):
        return "instance"

    async def status_porcelain(*args):
        return ""

    async def verdict(*args, **kwargs):
        raise LockHeld(Path("lock"), holder)

    published = []
    checkout = SimpleNamespace(
        repo=FakePath(),
        config=SimpleNamespace(state_dir=Path("state")),
        git=SimpleNamespace(describe=describe, status_porcelain=status_porcelain),
        clock=None,
        fs=None,
        journal=SimpleNamespace(read=lambda: []),
    )
    monkeypatch.setattr(entry, "Lockfile", FakeLock)
    monkeypatch.setattr(runner, "verdict", verdict)
    monkeypatch.setattr(entry.control, "read_active", lambda *args: ("lifecycle", None))
    monkeypatch.setattr(entry.control, "publish_request", lambda *args: published.append(args[1]))
    if route == "control":
        operation = entry._control(checkout, "stop")
    elif route == "verdict":
        operation = entry._verdict(checkout, "candidate", "confirm", None, True, False)
    else:
        operation = entry._retro(checkout, None)
    verb = (holder or {}).get("verb")
    if verb in {"drain", "serve"}:
        assert asyncio.run(operation) == 0
        assert len(published) == 1
    else:
        with pytest.raises(runner.Refusal, match=verb or "unknown holder"):
            asyncio.run(operation)
        assert published == []
