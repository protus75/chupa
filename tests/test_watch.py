import json
import os
import subprocess
import sys

import chupa.observe as watch


def test_queue_projection_and_fallback(tmp_path, monkeypatch):
    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    for stem, priority, dependency in [("old", "P1", "none"), ("new", "P2", "none"), ("blocked", "P0", "missing")]:
        path = tmp_path / "tickets" / stem / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\nstate: confirmed\npriority: {priority}\n---\n## Depends on\n- {dependency}\n")
    # The real format uses plain 'none', not a dependency named none.
    for stem in ("old", "new"):
        path = tmp_path / "tickets" / stem / "ticket.md"
        path.write_text(path.read_text().replace("- none", "none"))
    assert [row[1] for row in watch.queue(ctx, [], {}, set())] == ["blocked", "old", "new"]
    (tmp_path / "state").mkdir()
    (tmp_path / "state/queue.json").write_text(json.dumps({"at": "2026-01-01T00:00:00+00:00", "order": ["new", "old"], "runs_before": {"new": ["old"]}}))
    assert watch.queue(ctx, [], {}, set()) == [
        ("P2", "new", "ready, not run yet; runs before: old"),
        ("P1", "old", "ready, not run yet"),
        ("P0", "blocked", "waits on missing"),
    ]


def test_drain_processes_only_this_repo(tmp_path, monkeypatch):
    # Another host's drain runs from this venv with its own --config; only this checkout's drains count.
    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch.os, "readlink", lambda path: str(tmp_path))
    monkeypatch.setattr(watch, "started", lambda ctx, pid: pid)
    rows = [
        (30, 1, "/v/bin/python3 -m chupa --config config.yaml drain"),
        (10, 1, "/v/bin/python3 -m chupa drain"),
        (20, 1, "/v/bin/python3 -m chupa --config /elsewhere/config.yaml drain"),
        (40, 1, "/v/bin/python3 -m chupa serve"),
    ]
    assert watch.drain_processes(ctx, rows) == [10, 30]


def test_running_needs_a_live_lock_holder_that_journaled_it(tmp_path):
    # A killed drain leaves its lockfile and a journaled `running`; a later holder (review) must not revive it.
    started = "2026-11-06T15:44:00+00:00"
    last = {"stale": {"to": "running", "ts": "2026-11-06T14:50:00+00:00"}, "live": {"to": "running", "ts": "2026-11-06T15:45:00+00:00"}}
    assert watch.lock_holder(tmp_path) is None
    assert watch.running_stems(tmp_path, last) == []
    (tmp_path / "chupa.lock").write_text(json.dumps({"pid": os.getpid(), "started_at": started}))
    assert watch.running_stems(tmp_path, last) == ["live"]
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    (tmp_path / "chupa.lock").write_text(json.dumps({"pid": dead.pid, "started_at": started}))
    assert watch.lock_holder(tmp_path) is None
    assert watch.running_stems(tmp_path, last) == []


def test_queue_counts_a_split_dependency_met_by_its_successors(tmp_path, monkeypatch):
    # A rejected parent whose split successors all merged is settled for the drain, so dependents are not waiting on it.
    from chupa.rework import SUPERSEDES

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    path = tmp_path / "tickets" / "child" / "ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nstate: confirmed\npriority: P1\n---\n## Depends on\n- parent\n")
    events = [
        {"type": "state_transition", "ticket": "parent", "body": {"to": "rejected"}, "ts": "2026-01-01T00:00:00+00:00"},
        {"type": "signal", "ticket": "parent", "body": {"signal": SUPERSEDES, "successors": ["part"]}, "ts": "2026-01-01T00:00:01+00:00"},
        {"type": "state_transition", "ticket": "part", "body": {"to": "merged"}, "ts": "2026-01-01T00:00:02+00:00"},
    ]
    last_state = {e["ticket"]: e["body"] for e in events if e["type"] == "state_transition"}
    assert watch.queue(ctx, events, last_state, set()) == [("P1", "child", "ready, not run yet")]


def test_recent_steps_merges_engine_and_stage_events(tmp_path, monkeypatch):
    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    state = tmp_path / "state"
    state.mkdir()
    log = [
        {"ts": f"2026-01-01T00:00:0{i}+00:00", **event}
        for i, event in enumerate(
            [
                {"event": "engine_start", "verb": "drain", "pid": 41},
                {"event": "stage_start", "stem": "alpha", "surface": "implement"},
                {"event": "stage_end", "stem": "alpha", "surface": "implement", "outcome": "ok"},
                {"event": "engine_stop", "verb": "drain", "pid": 41, "outcome": "quiescent"},
                {"event": "stage_end", "stem": "alpha", "surface": "review", "outcome": "failed"},
                {"event": "engine_start", "verb": "serve", "pid": 42},
            ]
        )
    ]
    (state / "engine.log").write_text("".join(json.dumps(e) + "\n" for e in log))
    monkeypatch.setattr(watch, "processes", lambda ctx: [])
    rows = watch.recent_steps(state, log, 20)
    assert [(r["stem"], r["text"]) for r in rows] == [
        (None, "serve started (pid 42)"),
        (None, "serve ended without a stop record (killed?)"),
        ("alpha", "Review end (failed)"),
        (None, "drain stopped (quiescent)"),
        ("alpha", "Implement end (ok)"),
        ("alpha", "Implement start"),
        (None, "drain started (pid 41)"),
    ]
    assert [r["kind"] for r in rows] == ["engine_start", "engine_lost", "review_failed", "engine_stop", "implement_ok", "implement_start", "engine_start"]  # Each event has its own icon kind.
    assert [r["ts"] for r in rows] == sorted((r["ts"] for r in rows), reverse=True)
    lines = watch.text_snapshot(ctx).split("Recent steps:\n", 1)[1].splitlines()
    assert lines == [f"  {watch.clock(r['ts'])}  " + (f"{r['stem']}  " if r["stem"] else "") + r["text"] for r in rows]
    monkeypatch.setattr(watch, "lock_holder", lambda state: object())
    assert len(watch.recent_steps(state, log, 20)) == 6


def test_snapshot_verb_reads_config_state_dir(tmp_path, capsys):
    from pathlib import Path

    from chupa.__main__ import main

    config = tmp_path / "host.yaml"
    source = Path("config.yaml").read_text().replace("state_dir: .chupa/state", "state_dir: custom-state")
    config.write_text(source)
    state = tmp_path / "custom-state"
    state.mkdir()
    (state / "engine.log").write_text(json.dumps({"event": "engine_start", "verb": "serve", "pid": 719, "ts": "2026-01-01T00:00:00+00:00"}) + "\n")
    assert main(["--config", str(config), "snapshot"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["stateDir"] == str(state)
    assert any(row["text"] == "serve started (pid 719)" for row in result["steps"])


def test_observe_verbs_take_no_lock_and_write_nothing(tmp_path, capsys):
    from datetime import UTC, datetime
    from pathlib import Path

    from chupa.__main__ import main
    from chupa.lockfile import Lockfile

    config = tmp_path / "host.yaml"
    config.write_text(Path("config.yaml").read_text().replace("state_dir: .chupa/state", "state_dir: custom-state"))
    state = tmp_path / "custom-state"
    lock = Lockfile(state, instance_id="test", clock=lambda: datetime(2026, 1, 1, tzinfo=UTC))
    lock.acquire()
    try:
        (state / "engine.log").write_text(json.dumps({"event": "engine_stop", "verb": "serve", "outcome": "stopped", "ts": "2026-01-01T00:00:00+00:00"}) + "\n")
        before = {p.relative_to(state): p.read_bytes() for p in state.rglob("*") if p.is_file()}
        assert main(["--config", str(config), "snapshot"]) == 0
        assert main(["--config", str(config), "watch", "--once"]) == 0
        after = {p.relative_to(state): p.read_bytes() for p in state.rglob("*") if p.is_file()}
        assert after == before
        assert "serve stopped (stopped)" in capsys.readouterr().out
    finally:
        lock.release()


def test_snapshot_lock_holder(tmp_path, monkeypatch):
    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    monkeypatch.setattr(watch, "processes", lambda ctx: [(712, 1, "python -m chupa --config x.yaml review stem")])
    monkeypatch.setattr(watch.os, "kill", lambda pid, signal: None)
    assert watch.snapshot(ctx)["lock"] == ""  # A missing lockfile is not a live holder.
    started_at = "2026-11-06T07:19:00+00:00"
    (tmp_path / "chupa.lock").write_text(json.dumps({"pid": 712, "started_at": started_at}))

    def dead(pid, signal):
        raise ProcessLookupError

    monkeypatch.setattr(watch.os, "kill", dead)
    assert watch.snapshot(ctx)["lock"] == ""  # A stale lockfile is not a live holder.
    monkeypatch.setattr(watch.os, "kill", lambda pid, signal: None)
    assert watch.snapshot(ctx)["lock"] == f"review since {watch.clock(started_at)} (pid 712)"
    monkeypatch.setattr(watch, "processes", lambda ctx: [(712, 1, "python -m chupa")])
    assert watch.snapshot(ctx)["lock"] == f"chupa since {watch.clock(started_at)} (pid 712)"
    monkeypatch.setattr(watch, "processes", lambda ctx: [(713, 1, "python -m chupa drain")])
    assert watch.snapshot(ctx)["lock"] == f"chupa since {watch.clock(started_at)} (pid 712)"


def test_snapshot_display_fields(tmp_path, monkeypatch):
    from datetime import datetime
    from types import SimpleNamespace

    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    ts = "2026-01-01T00:00:00+00:00"
    now = datetime.fromisoformat("2026-01-03T03:00:00+00:00")
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    monkeypatch.setattr(watch, "datetime", FixedDateTime)
    ticket = lambda stem: SimpleNamespace(stem=stem, frontmatter=SimpleNamespace(priority="P1", state="confirmed"), depends=(), runs_before=(), sections={"Goal / Why": "goal"})
    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: ({s: ticket(s) for s in ("live", "waiting")}, {}))
    events = [
        {"type": "state_transition", "ticket": "live", "body": {"to": "running"}, "ts": ts},
        {"type": "state_transition", "ticket": "done", "body": {"to": "merged", "commit": "abc"}, "ts": ts},
    ]
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)
    monkeypatch.setattr(watch, "running_stems", lambda *args: ["live"])
    monkeypatch.setattr(watch, "lock_holder", lambda state: None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {"abc": {"date": "2026-01-03T02:00:00+00:00", "subject": "change"}})
    (tmp_path / "engine.log").write_text(json.dumps({"event": "stage_start", "stem": "live", "surface": "implement", "ts": ts}) + "\n")
    snap = watch.snapshot(ctx)
    rows = {r["stem"]: r for r in snap["rows"]}
    assert snap["priorities"] == ["P0", "P1", "P2", "P3"]  # A copied or missing priority vocabulary differs.
    assert snap["counts"] == {"blocked": 0, "queued": 1, "running": 1, "merged": 1}  # Counting only open rows loses the merged row.
    assert rows["live"]["runsBeforeChoices"] == ["waiting"]  # The current and merged stems are excluded.
    assert rows["waiting"]["runsBeforeChoices"] == ["live"]  # Choices are specific to each row.
    assert snap["runningStem"] == "live"  # A missing running fallback loses the active ticket.
    assert snap["verdictCommands"] == {"confirm": ["confirm", "--yes"], "reject": ["reject", "--yes"]}  # Both noninteractive verbs need their flag.
    assert rows["done"]["mergedAtAgo"] == "2 days ago"  # Settlement time differs from commit time.
    assert rows["done"]["commit"]["dateAgo"] == "1 hr ago"  # Commit time must not reuse settlement time.
    assert rows["done"]["mergedAtDisplay"] == watch.local(ts).strftime("%x, %X")  # Settlement date uses its own timestamp.
    assert rows["done"]["commit"]["dateDisplay"] == watch.local("2026-01-03T02:00:00+00:00").strftime("%x, %X")  # Commit date uses the commit timestamp.
    step = snap["steps"][0]
    assert step["timeDisplay"] == watch.clock(ts)  # Tree labels use the event time.
    assert step["dateDisplay"] == watch.local(ts).strftime("%x, %X")  # Tooltips use the event date.
    monkeypatch.setattr(watch, "running_stems", lambda *args: [])
    assert watch.snapshot(ctx)["runningStem"] is None  # A previous running stem must not persist.


def test_diagnose_prompt_uses_live_running_state(tmp_path, monkeypatch, capsys):
    from chupa.__main__ import main
    from tests.test_config import VALID

    (tmp_path / "config.yaml").write_text(VALID)
    path = tmp_path / "tickets/live/ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text("ticket")
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: [{"type": "state_transition", "ticket": "live", "body": {"to": "running"}, "ts": "2026-01-01T00:00:00+00:00"}])
    monkeypatch.setattr(watch, "lock_holder", lambda state: watch.datetime.fromisoformat("2025-12-31T00:00:00+00:00"))
    assert main(["prompt", "diagnose", "live"], cwd=tmp_path) == 0  # The CLI accepts the ticket.
    running = capsys.readouterr().out
    assert main(["prompt", "running", "live"], cwd=tmp_path) == 0
    assert running == capsys.readouterr().out  # Diagnose selects the actual running template.
    monkeypatch.setattr(watch, "lock_holder", lambda state: None)
    assert main(["prompt", "diagnose", "live"], cwd=tmp_path) == 0
    assert capsys.readouterr().out != running  # A stale journal entry keeps the diagnose template.


def test_snapshot_step_files_and_mechanical_kinds(tmp_path, monkeypatch):
    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    directory = tmp_path / "tickets" / "alpha"
    directory.mkdir(parents=True)
    (directory / "run.md").write_text("run")
    (directory / "checks.json").write_text("checks")
    events = [
        {"event": "stage_start", "stem": "alpha", "surface": surface, "ts": f"2026-01-01T00:00:0{i}+00:00"}
        for i, surface in enumerate(("implement", "check", "merge"))
    ]
    (tmp_path / "engine.log").write_text("".join(json.dumps(e) + "\n" for e in events))
    rows = {row["text"]: row for row in watch.snapshot(ctx)["steps"]}
    assert rows["Implement start"]["path"] == "tickets/alpha/run.md"  # The ticket file is a different target.
    assert (rows["Check start"]["kind"], rows["Check start"]["path"]) == ("check_start", "tickets/alpha/checks.json")  # Generic stage kind or ticket path is wrong.
    assert watch.current_step(events, "alpha") == ("Merge", events[-1]["ts"], None)  # A model surface would display model details.
    (directory / "run.md").unlink()
    rows = {row["text"]: row for row in watch.snapshot(ctx)["steps"]}
    assert rows["Implement start"]["path"] == "tickets/alpha/ticket.md"  # A missing run record must not be opened.
    assert watch.current_step([dict(events[1], event="stage_end", outcome="ok")], "alpha")[0] == "Review"  # Check advances to Review.
