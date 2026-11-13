import asyncio

import pytest

from chupa import observe, runner
from chupa.__main__ import main
from chupa.journal import EventType
from chupa.lockfile import Lockfile, LockHeld
from tests.integration.test_cli import ENV
from tests.integration.test_drain import Clock, commit_ticket, confirmed, journal, make_root
from tests.integration.test_git import commit_lock


@pytest.fixture
def stopped(tmp_path):
    root = make_root(tmp_path)
    commit_ticket(root, "stale", confirmed())
    journal(root).append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="stale")
    return root


def invoke(root, *args):
    return main(list(args), cwd=root, env=ENV, clock=Clock())


def transitions(root):
    return [e.body["to"] for e in journal(root).read() if e.type == EventType.STATE_TRANSITION and e.ticket == "stale"]


def test_reject_reaps_a_killed_run(stopped, capsys):
    assert invoke(stopped, "reject", "--yes", "stale") == 0
    assert transitions(stopped)[-2:] == ["abandoned", "rejected"]
    assert "state: rejected" in (stopped / "tickets/stale/ticket.md").read_text()
    assert "is running" not in capsys.readouterr().err


def test_confirm_reaps_then_refuses(stopped, capsys):
    before = (stopped / "tickets/stale/ticket.md").read_text()
    assert invoke(stopped, "confirm", "--yes", "stale") == 2
    assert "is neither a draft nor in the Reject queue" in capsys.readouterr().err
    assert transitions(stopped)[-1] == "abandoned"
    assert (stopped / "tickets/stale/ticket.md").read_text() == before


def test_order_beside_dead_run(stopped, monkeypatch, capsys):
    monkeypatch.setattr(observe, "lock_holder", lambda _, *args: object())
    assert invoke(stopped, "order", "stale", "--priority", "P0") == 2
    assert "is running" in capsys.readouterr().err
    monkeypatch.setattr(observe, "lock_holder", lambda _, *args: None)
    assert invoke(stopped, "order", "stale", "--priority", "P0") == 0
    assert "priority: P0" in (stopped / "tickets/stale/ticket.md").read_text()


def test_status_shows_interrupted(stopped, monkeypatch, capsys):
    assert invoke(stopped, "status") == 0
    sections = dict(block.split("\n", 1) for block in capsys.readouterr().out.strip().split("\n\n"))
    assert "- stale" in sections["interrupted (the engine stopped mid-run; reject it, or start the engine to rerun it):"]
    assert "stale" not in sections["in flight:"]
    monkeypatch.setattr(observe, "lock_holder", lambda _, *args: object())
    assert invoke(stopped, "status") == 0
    assert "in flight:\n- stale" in capsys.readouterr().out


def test_reject_refuses_a_live_run(stopped):
    from types import SimpleNamespace

    from chupa.config import load_config
    from chupa.git import Git
    from chupa.seams import LocalFileSystem, SubprocessExec

    config = load_config(None, cwd=stopped)
    checkout = SimpleNamespace(
        config=config, git=Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(stopped / ".chupa/state")), repo=stopped, clock=Clock(), journal=journal(stopped), fs=LocalFileSystem()
    )
    lock = Lockfile(config.state_dir, verb="drain", instance_id="test", clock=checkout.clock)
    lock.acquire()
    try:
        with pytest.raises(LockHeld):
            asyncio.run(runner.verdict("stale", checkout, kill=True))
    finally:
        lock.release()
    assert transitions(stopped) == ["running"]


def test_menu_offers_reject_for_dead_run(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from tests.unit.test_menu_admission import fake_snapshot_inputs
    from tests.unit.test_stale_running import held_events

    monkeypatch.setattr(observe, "ticket_menu_inputs", fake_snapshot_inputs)
    ctx = observe.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    ticket = SimpleNamespace(stem="stale", frontmatter=SimpleNamespace(priority="P1", state="confirmed"), depends=(), runs_before=(), sections={})
    events = [{"type": "state_transition", "ticket": "stale", "body": {"to": "running"}, "ts": "2026-01-01T00:00:00+00:00"}]
    monkeypatch.setattr(observe, "journal", lambda *a, **kw: events)
    monkeypatch.setattr(observe, "load_tickets", lambda *a: ({"stale": ticket}, {}))
    monkeypatch.setattr(observe, "held", lambda *a: set())
    monkeypatch.setattr(observe, "operator_holds", lambda *a: set())
    monkeypatch.setattr(observe, "running_stems", lambda *a: [])
    monkeypatch.setattr(observe, "uncommitted_tickets", lambda *a: (set(), set()))
    monkeypatch.setattr(observe, "committed_ticket_shas", lambda *a: {"stale": "sha"})
    monkeypatch.setattr(observe, "commits", lambda *a: {})
    monkeypatch.setattr(observe, "lock_holder", lambda _, *args: None)
    menu = observe.snapshot(ctx)["rows"][0]["menu"]
    assert (menu["chupaReject"], menu["chupaConfirm"]) == ("on", "off")

    async def clean(git, repo, stem):
        return False

    monkeypatch.setattr(runner, "ticket_pending", clean)
    monkeypatch.setattr(observe, "lock_holder", lambda _, *args: object())
    menu = observe.snapshot(ctx)["rows"][0]["menu"]
    assert (menu["chupaReject"], menu["chupaConfirm"]) == ("off", "off")
    monkeypatch.setattr(observe, "lock_holder", lambda _, *args: None)
    events[:] = [dict(type=e.type, ticket=e.ticket, body=e.body, ts=e.ts, key=e.key) for e in held_events("stale")]
    menu = observe.snapshot(ctx)["rows"][0]["menu"]
    assert (menu["chupaReject"], menu["chupaConfirm"]) == ("off", "off")


def test_every_locked_verb_reaps(stopped, monkeypatch):
    calls = []

    async def reap(checkout):
        with pytest.raises(LockHeld):
            lock = Lockfile(checkout.config.state_dir, verb="drain", instance_id="probe", clock=checkout.clock)
            lock.acquire()
        calls.append("reap")
        raise RuntimeError("stopped after reap")

    monkeypatch.setattr(runner, "reap", reap)
    path = stopped / "tickets/stale/ticket.md"
    path.write_text(path.read_text() + "\n")
    for args in (("dismiss", "id"), ("triage",), ("retro",), ("reject", "--yes", "stale")):
        calls.clear()
        with pytest.raises(RuntimeError, match="stopped after reap"):
            invoke(stopped, *args)
        assert calls == ["reap"]
    # Restore the committed ticket using its known original contents.
    path.write_text(confirmed())
    calls.clear()
    # Clean review can proceed without taking the lock; stop at its first model setup.
    from chupa import __main__ as entry

    monkeypatch.setattr(entry, "build_control", lambda *_: (_ for _ in ()).throw(RuntimeError("review reached model")))
    with pytest.raises(RuntimeError, match="review reached model"):
        invoke(stopped, "review", "stale")
    assert calls == []
    for verb in ("kill", "stop", "pause", "resume"):
        invoke(stopped, verb)
        assert calls == []
