import asyncio
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from chupa import runner, status
from chupa.journal import EventType


def event(kind, body, ticket="x", key=None):
    return SimpleNamespace(type=kind, body=body, ticket=ticket, key=key, ts="2026-01-01T00:00:00+00:00")


def test_project_interrupted():
    events = [event(EventType.STATE_TRANSITION, {"to": "running"})]
    dead = status.project(events, alive=False)
    live = status.project(events, alive=True)
    assert dead.interrupted == ("x",) and dead.in_flight == ()
    assert live.in_flight == ("x",) and live.interrupted == ()
    projected = status.project(held_events(), alive=False)
    assert projected.in_flight == ("x",) and projected.interrupted == ()


def test_render_interrupted_block():
    view = status.project([event(EventType.STATE_TRANSITION, {"to": "running"})], alive=False)
    text = status.render(view)
    assert "in flight:\n(none)\n\ninterrupted (the engine stopped mid-run; reject it, or start the engine to rerun it):\n- x" in text
    assert "interrupted (" not in status.render(status.project([]))


def test_reap_reconciles_with_harvest(monkeypatch):
    events = [event(EventType.STATE_TRANSITION, {"to": "running"}, "exists"), event(EventType.STATE_TRANSITION, {"to": "running"}, "missing")]

    class Journal:
        def read(self):
            return list(events)

        def append(self, kind, body, *, ticket=None, key=None):
            events.append(event(kind, body, ticket, key))

    monkeypatch.setattr(Path, "exists", lambda path: path.name == "exists")
    harvest = AsyncMock()
    monkeypatch.setattr(runner, "harvest_orphan", harvest)
    git = SimpleNamespace(worktree_remove=AsyncMock(), worktree_prune=AsyncMock())
    checkout = SimpleNamespace(config=SimpleNamespace(worktree_root=Path("/work")), journal=Journal(), git=git, repo=Path("/repo"))
    assert asyncio.run(runner.reap(checkout)) == ["exists", "missing"]
    harvest.assert_awaited_once_with(checkout, "exists", 0)
    git.worktree_remove.assert_awaited_once_with(Path("/repo"), Path("/work/exists"))
    git.worktree_prune.assert_awaited_once_with(Path("/repo"))
    assert [e.ticket for e in events if e.type == EventType.STATE_TRANSITION and e.body["to"] == "abandoned"] == ["exists", "missing"]


def test_verdict_reaps_before_verdict_locked(monkeypatch):
    calls = []

    class Lock:
        def __init__(self, *args, **kwargs):
            pass

        def acquire(self):
            calls.append("acquire")

        def release(self):
            calls.append("release")

    async def reap(checkout):
        calls.append("reap")

    async def verdict(*args, **kwargs):
        calls.append("verdict")
        return 7

    monkeypatch.setattr(runner, "Lockfile", Lock)
    monkeypatch.setattr(runner, "reap", reap)
    monkeypatch.setattr(runner, "verdict_locked", verdict)
    checkout = SimpleNamespace(config=SimpleNamespace(state_dir=Path("/state")), git=SimpleNamespace(describe=AsyncMock(return_value="id")), repo=Path("/repo"), clock=object())
    assert asyncio.run(runner.verdict("xx", checkout, kill=True)) == 7
    assert calls == ["acquire", "reap", "verdict", "release"]


def held_events(stem="x"):
    sha = "a" * 40
    receipt = dict(stem=stem, attempt=0, reviewed_sha=sha, candidate_base_sha=sha, candidate_sha=sha, checked_tree=sha, review_provider=None, review_model=None, admission="HELD", reason="go_absent")
    return [event(EventType.STATE_TRANSITION, {"to": "running"}, stem), event(EventType.EFFECT_COMPLETION, {"result": receipt}, stem, f"merge-regate/{stem}/0/{sha}/{sha}")]


def test_order_refuses_only_a_live_running_stem(monkeypatch):
    import pytest

    from chupa import __main__ as entry

    class PathFake:
        def __truediv__(self, other):
            return self

        def is_file(self):
            return True

        def read_bytes(self):
            return b"original"

    path = PathFake()
    history = [event(EventType.STATE_TRANSITION, {"to": "running"}, "sample")]
    checkout = SimpleNamespace(repo=path, config=SimpleNamespace(state_dir=path), journal=SimpleNamespace(read=lambda: history), fs=SimpleNamespace(write=lambda p, b: writes.append(b)))
    writes = []
    monkeypatch.setattr(entry, "order", lambda *a, **kw: "changed")
    monkeypatch.setattr(entry, "validate_ticket", lambda *a: SimpleNamespace(frontmatter=SimpleNamespace(priority="P0")))
    monkeypatch.setattr(entry.observe, "lock_holder", lambda _: object())
    with pytest.raises(runner.Refusal, match="is running"):
        entry._order(checkout, "sample", "P0", None)
    monkeypatch.setattr(entry.observe, "lock_holder", lambda _: None)
    assert entry._order(checkout, "sample", "P0", None) == 0
    assert writes == [b"changed"]
    history[:] = held_events("sample")
    with pytest.raises(runner.Refusal, match="is running"):
        entry._order(checkout, "sample", "P0", None)
    assert writes == [b"changed"]


def test_status_verb_passes_alive(monkeypatch):
    from chupa import __main__ as entry
    from chupa import retro, specs

    calls = []

    class SpecPath:
        def __truediv__(self, name):
            return self

        def read_text(self):
            return "fixed spec"

    monkeypatch.setattr(runner, "SPECS_DIR", SpecPath())
    monkeypatch.setattr(specs, "load_spec", lambda text: SimpleNamespace(meta=SimpleNamespace(version="v")))
    monkeypatch.setattr(entry.observe, "lock_holder", lambda _: holder[0])
    monkeypatch.setattr(entry, "project", lambda events, **kw: calls.append(kw["alive"]))
    monkeypatch.setattr(retro, "production_evidence", AsyncMock())
    checkout = SimpleNamespace(
        journal=SimpleNamespace(read=lambda: []),
        git=SimpleNamespace(rev_parse=AsyncMock(return_value="sha")),
        repo=Path("/repo"),
        clock=lambda: datetime(2026, 1, 1, tzinfo=UTC),
        config=SimpleNamespace(state_dir=Path("/state"), box_policy=None),
        fs=object(),
    )
    holder = [None]
    asyncio.run(entry._status(checkout))
    holder[0] = object()
    asyncio.run(entry._status(checkout))
    assert calls == [False, True]


def test_locked_verbs_reap_after_acquire(monkeypatch):
    import pytest

    from chupa import __main__ as entry

    class Stop(Exception):
        pass

    calls = []

    class Lock:
        def __init__(self, *args, **kwargs):
            pass

        def acquire(self):
            calls.append("acquire")

        def release(self):
            calls.append("release")

    class Git:
        def __init__(self, *args, **kwargs):
            pass

        async def describe(self, repo):
            return "id"

        async def status_porcelain(self, *args):
            return "dirty"

    async def reap(checkout):
        calls.append("reap")
        raise Stop

    monkeypatch.setattr(entry, "Lockfile", Lock)
    monkeypatch.setattr(entry, "Git", Git)
    monkeypatch.setattr(runner, "reap", reap)
    checkout = SimpleNamespace(config=SimpleNamespace(state_dir=Path("/state")), git=Git(), repo=Path("/repo"), clock=object(), control=None)
    for call in (lambda: asyncio.run(entry._retro(checkout, None)),):
        calls.clear()
        with pytest.raises(Stop):
            call()
        assert calls == ["acquire", "reap", "release"]
    monkeypatch.setattr(entry, "load_config", lambda *a, **kw: checkout.config)
    monkeypatch.setattr(entry, "child_env", lambda env, config: env)
    for args in (["dismiss", "id"], ["triage"]):
        calls.clear()
        with pytest.raises(Stop):
            entry.main(args, cwd=Path("/repo"), env={})
        assert calls == ["acquire", "reap", "release"]
