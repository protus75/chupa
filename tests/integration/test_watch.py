import json
import os
import subprocess
import sys

import pytest

import chupa.observe as watch


@pytest.fixture(autouse=True)
def config_fixture(tmp_path):
    from tests.integration.test_config import VALID

    (tmp_path / "config.yaml").write_text(VALID)


@pytest.fixture(autouse=True)
def snapshot_inputs(monkeypatch):
    from tests.unit.test_menu_admission import fake_snapshot_inputs

    real = watch.ticket_menu_inputs
    monkeypatch.setattr(watch, "ticket_menu_inputs", lambda ctx, *args: fake_snapshot_inputs(ctx, *args) if ctx.git is None else real(ctx, *args))


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
    assert [row[1] for row in watch.queue(ctx, [], {}, set(), set())] == ["blocked", "old", "new"]
    (tmp_path / "state").mkdir()
    (tmp_path / "state/queue.json").write_text(json.dumps({"at": "2026-01-01T00:00:00+00:00", "order": ["new", "old"], "runs_before": {"new": ["old"]}}))
    assert watch.queue(ctx, [], {}, set(), set()) == [
        ("P2", "new", "ready, not run yet; runs before: old"),
        ("P1", "old", "ready, not run yet"),
        ("P0", "blocked", "waits on missing"),
    ]


def test_text_snapshot_folds_the_whole_journal(tmp_path, monkeypatch):
    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    for stem in ("merged-old", "still-ready"):
        ticket = tmp_path / "tickets" / stem / "ticket.md"
        ticket.parent.mkdir(parents=True)
        ticket.write_text("---\nstate: confirmed\npriority: P1\n---\n## Depends on\nnone\n")
    journal = ctx.state / "journal"
    journal.mkdir(parents=True)
    merged = {"type": "state_transition", "ticket": "merged-old", "body": {"to": "merged"}, "ts": "2026-01-01T00:00:00+00:00"}
    (journal / "000001.jsonl").write_text(json.dumps(merged) + "\n")
    (journal / "000002.jsonl").write_text((json.dumps({"type": "signal", "body": {}}) + "\n") * 20001)
    monkeypatch.setattr(watch, "processes", lambda ctx: [])
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    queue = watch.text_snapshot(ctx).split("Queue (", 1)[1]
    assert "still-ready  ready, not run yet" in queue  # The queue must actually include pending tickets.
    assert "merged-old" not in queue  # A truncated journal incorrectly queues the merged ticket.


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
    assert watch.queue(ctx, events, last_state, set(), set()) == [("P1", "child", "ready, not run yet")]


def test_recent_steps_rework_and_retro_kinds(tmp_path):
    log = [
        {"ts": f"2026-01-01T00:00:0{i}+00:00", "event": event, "stem": "alpha", "surface": surface, **({"outcome": outcome} if outcome else {})}
        for i, (event, surface, outcome) in enumerate([("stage_start", "rework", None), ("stage_end", "rework", "ok"), ("stage_start", "retro", None), ("stage_end", "retro", "failed")])
    ]
    rows = watch.recent_steps(tmp_path, log, 20)
    assert [r["kind"] for r in rows] == ["retro_failed", "retro_start", "rework_ok", "rework_start"]  # A generic stage kind loses the step's icon.


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
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    lines = watch.text_snapshot(ctx).split("Recent steps:\n", 1)[1].splitlines()
    assert lines == [f"  {watch.clock(r['ts'])}  " + (f"{r['stem']}  " if r["stem"] else "") + r["text"] for r in rows]
    monkeypatch.setattr(watch.os, "kill", lambda pid, signal: None)
    (state / "chupa.lock").write_text(json.dumps({"pid": 42, "started_at": log[-1]["ts"]}))
    matching = watch.recent_steps(state, log, 20)
    assert len(matching) == 6 and all(r["kind"] != "engine_lost" for r in matching)
    (state / "chupa.lock").write_text(json.dumps({"pid": 43, "started_at": log[-1]["ts"]}))
    different = watch.recent_steps(state, log, 20)
    assert len(different) == 7
    assert [(r["stem"], r["text"]) for r in different if r["kind"] == "engine_lost"] == [(None, "serve ended without a stop record (killed?)")]


def test_recent_steps_triage_message_number():
    log = [
        {"ts": f"2026-01-01T00:00:0{i}+00:00", "stem": "triage", "surface": "triage", **event}
        for i, event in enumerate(
            [
                {"event": "stage_start", "run_seq": 337},
                {"event": "stage_end", "run_seq": 337, "outcome": "ok"},
                {"event": "stage_start"},
                {"event": "stage_end", "run_seq": 337, "outcome": "failed"},
            ]
        )
    ]
    rows = watch.recent_steps(None, log, 10)
    assert [(row["kind"], row["text"]) for row in rows] == [
        ("triage_failed", "Triage #337 end (failed)"),
        ("triage_start", "Triage start"),
        ("triage_ok", "Triage #337 end (ok)"),
        ("triage_start", "Triage #337 start"),
    ]  # Generic kinds, missing numbers, or a missing legacy label differ.


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
    assert result["configPath"] == str(config.resolve())  # The default config path is a different file.
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
    lock = Lockfile(state, verb="drain", instance_id="test", clock=lambda: datetime(2026, 1, 1, tzinfo=UTC))
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
    snap = watch.snapshot(ctx)
    assert snap["lock"] == "" and snap["engine"] is False  # A missing lockfile is not a live holder.
    started_at = "2026-11-06T07:19:00+00:00"
    (tmp_path / "chupa.lock").write_text(json.dumps({"pid": 712, "started_at": started_at}))

    def dead(pid, signal):
        raise ProcessLookupError

    monkeypatch.setattr(watch.os, "kill", dead)
    snap = watch.snapshot(ctx)
    assert snap["lock"] == "" and snap["engine"] is False  # A stale lockfile is not a live holder.
    monkeypatch.setattr(watch.os, "kill", lambda pid, signal: None)
    for args, verb, engine in [
        ("python -m chupa triage", "triage", False),
        ("python -m chupa drain --detach", "drain", True),
        ("python -m chupa --config c.yaml serve", "serve", True),
        ("python -m chupa --config x.yaml review stem", "review", False),
    ]:
        (tmp_path / "chupa.lock").write_text(json.dumps({"pid": 712, "started_at": started_at, "verb": verb}))
        monkeypatch.setattr(watch, "processes", lambda ctx: [(712, 1, "python -m chupa drain")])
        snap = watch.snapshot(ctx)
        assert snap["lock"] == f"{verb} since {watch.clock(started_at)} (pid 712)"  # The tooltip identifies the actual holder.
        assert snap["engine"] is engine  # Only drain and serve can receive Stop.
    (tmp_path / "chupa.lock").write_text(json.dumps({"pid": 712, "started_at": started_at}))
    monkeypatch.setattr(watch, "processes", lambda ctx: [(712, 1, "python -m chupa")])
    snap = watch.snapshot(ctx)
    assert snap["lock"] == f"chupa since {watch.clock(started_at)} (pid 712)" and snap["engine"] is False  # An unknown verb cannot be stopped.
    monkeypatch.setattr(watch, "processes", lambda ctx: [(713, 1, "python -m chupa drain")])
    snap = watch.snapshot(ctx)
    assert snap["lock"] == f"chupa since {watch.clock(started_at)} (pid 712)" and snap["engine"] is False  # An unknown verb cannot be stopped.


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

    def ticket(stem):
        return SimpleNamespace(
            stem=stem,
            frontmatter=SimpleNamespace(priority="P1", state="confirmed"),
            depends=(),
            runs_before=("waiting",) if stem == "live" else (),
            sections={"Goal / Why": "goal" if stem == "live" else ""},
        )

    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: ({s: ticket(s) for s in ("live", "waiting")}, {}))
    events = [
        {"type": "state_transition", "ticket": "live", "body": {"to": "running"}, "ts": ts},
        {"type": "state_transition", "ticket": "done", "body": {"to": "merged", "commit": "abc"}, "ts": ts},
    ]
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)
    monkeypatch.setattr(watch, "running_stems", lambda *args: ["live"])
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {"abc": {"date": "2026-01-03T02:00:00+00:00", "subject": "change", "short": "abc", "author": "Ada"}})
    (tmp_path / "engine.log").write_text(json.dumps({"event": "stage_start", "stem": "live", "surface": "implement", "ts": ts}) + "\n")
    snap = watch.snapshot(ctx)
    rows = {r["stem"]: r for r in snap["rows"]}
    assert snap["watch"] == [
        {"base": str(tmp_path.resolve()), "glob": "tickets/*/ticket.md"},
        {"base": str(tmp_path.resolve()), "glob": "{journal/*.jsonl,queue.json,engine.log,box/*.json}"},
    ]  # Both locations must be watched.
    assert len(snap["engineVerbs"]) == 6 and snap["engineVerbs"][0] == {
        "label": "Drain",
        "detail": "Run every eligible ticket to quiescence, then exit.",
        "argv": ["drain", "--detach"],
    }  # The menu must not be empty or reordered.
    assert snap["drainCommand"] == ["drain", "--detach"]
    assert rows["live"]["priorityChoices"] == [{"label": p, "description": "current" if p == "P1" else ""} for p in ("P0", "P1", "P2", "P3")]  # Only the actual priority is current.
    assert {item["heading"] for item in rows["done"]["detail"]} == {None, "Commit"}  # Merged rows do not show open fields.
    assert {"heading": None, "text": f"settled 2 days ago ({watch.local(ts).strftime('%x, %X')})"} in rows["done"]["detail"]  # Settlement uses its own timestamp.
    assert {item["heading"] for item in rows["live"]["detail"]} == {None, "Goal / Why", "Runs before"}  # Open rows do not show a commit.
    assert {"heading": "Goal / Why", "text": "(none)"} in rows["waiting"]["detail"]  # Empty goals have a visible placeholder.
    assert {"heading": "Runs before", "text": "(none)"} in rows["waiting"]["detail"]  # Empty ordering has a visible placeholder.
    assert snap["priorities"] == ["P0", "P1", "P2", "P3"]  # A copied or missing priority vocabulary differs.
    assert snap["counts"] == {"blocked": 0, "queued": 1, "running": 1, "merged": 1}  # Counting only open rows loses the merged row.
    assert rows["live"]["runsBeforeChoices"] == [{"label": "waiting", "picked": True}]  # The current and merged stems are excluded.
    assert rows["waiting"]["runsBeforeChoices"] == [{"label": "live", "picked": False}]  # Choices are specific to each row.
    assert snap["runningStem"] == "live"  # A missing running fallback loses the active ticket.
    assert snap["verdictCommands"] == {"confirm": ["confirm", "--extension"], "reject": ["reject", "--extension"]}  # Both noninteractive verbs need their flag.
    assert rows["done"]["mergedAtAgo"] == "2 days ago"  # Settlement time differs from commit time.
    assert rows["done"]["commit"]["dateAgo"] == "1 hr ago"  # Commit time must not reuse settlement time.
    assert rows["done"]["mergedAtDisplay"] == watch.local(ts).strftime("%x, %X")  # Settlement date uses its own timestamp.
    assert rows["done"]["commit"]["dateDisplay"] == watch.local("2026-01-03T02:00:00+00:00").strftime("%x, %X")  # Commit date uses the commit timestamp.
    step = snap["steps"][0]
    assert step["timeDisplay"] == watch.clock(ts)  # Tree labels use the event time.
    assert step["dateDisplay"] == watch.local(ts).strftime("%x, %X")  # Tooltips use the event date.
    monkeypatch.setattr(watch, "running_stems", lambda *args: [])
    assert watch.snapshot(ctx)["runningStem"] is None  # A previous running stem must not persist.


def test_snapshot_menu_availability(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from chupa.box import Box, Resolution
    from chupa.seams import LocalFileSystem

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    tickets = {
        stem: SimpleNamespace(stem=stem, frontmatter=SimpleNamespace(priority="P1", state="confirmed"), depends=deps, runs_before=(), sections={})
        for stem, deps in (("held", ("missing",)), ("ready", ()), ("held-ready", ()))
    }
    events = [{"type": "state_transition", "ticket": "done", "body": {"to": "merged"}, "ts": "2026-01-01T00:00:00+00:00"}]
    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: (tickets, {"invalid": "bad ticket"}))
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)
    monkeypatch.setattr(watch, "held", lambda history, blobs: {"held", "held-ready"})
    monkeypatch.setattr(watch, "operator_holds", lambda ctx, history: set())
    monkeypatch.setattr(watch, "running_stems", lambda *args: [])
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {stem: "sha" for stem in tickets})
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    box = Box(ctx.state / "box", LocalFileSystem())
    pending, _ = box.enqueue(message_class="suggestion", origin="operator", summary="Pending")
    resolved, _ = box.enqueue(message_class="suggestion", origin="operator", summary="Resolved")
    box.resolve(resolved, Resolution(kind="ticket", link="done"))

    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: object())
    snap = watch.snapshot(ctx)
    rows = {row["stem"]: row for row in snap["rows"]}
    assert (rows["held"]["menu"]["chupaConfirm"], rows["held"]["menu"]["chupaRun"]) == ("off", "off")  # A content park alone cannot be confirmed; unmet dependencies block Run.
    assert (rows["held-ready"]["menu"]["chupaRun"], rows["ready"]["menu"]["chupaRun"], rows["ready"]["menu"]["chupaReview"]) == (
        "locked",
        "locked",
        "on",
    )  # Run needs the lock, while committed review does not.
    assert (rows["invalid"]["menu"]["chupaReview"], rows["invalid"]["menu"]["chupaPriority"]) == ("off", "off")  # Invalid blocked rows cannot be reviewed or ordered.
    assert rows["ready"]["menu"]["chupaReject"] == "on"
    assert rows["done"]["menu"]["chupaLint"] == "off"  # Merged rows cannot be linted.
    box_rows = {row["id"]: row for row in snap["box"]}
    assert box_rows[pending]["menu"] == {"chupaTriage": "locked", "chupaDismiss": "locked"}  # Pending actions require the lock.
    assert box_rows[resolved]["menu"] == {"chupaTriage": "off", "chupaDismiss": "off"}  # Resolved actions are unavailable even when locked.

    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: ({"held"}, set()))
    dirty = {row["stem"]: row for row in watch.snapshot(ctx)["rows"]}
    assert (dirty["held"]["menu"]["chupaConfirm"], dirty["held"]["menu"]["chupaReject"]) == ("off", "on")  # Intake does not make a content park confirmable.
    assert dirty["held"]["menu"]["chupaReview"] == "on"  # Dirty review runs intake without the engine lock.
    assert dirty["invalid"]["menu"]["chupaReview"] == "off"  # Invalid rows remain unavailable.
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: None)
    snap = watch.snapshot(ctx)
    stopped = {row["stem"]: row for row in snap["rows"]}
    assert (stopped["held"]["menu"]["chupaConfirm"], stopped["held"]["menu"]["chupaReject"]) == ("off", "on")  # A content park is rejectable but not confirmable.
    assert (stopped["ready"]["menu"]["chupaRun"], stopped["ready"]["menu"]["chupaReview"]) == ("on", "on")  # Runnable and reviewable work is unlocked.
    assert stopped["held"]["menu"]["chupaReview"] == "on"  # Dirty review can intake when the lock is free.
    assert stopped["invalid"]["menu"]["chupaReview"] == "off"  # Stopping the engine does not validate a ticket.
    assert stopped["held-ready"]["menu"]["chupaRun"] == "on"  # A held runnable ticket remains runnable without the lock.
    assert next(row for row in snap["box"] if row["id"] == pending)["menu"] == {"chupaTriage": "on", "chupaDismiss": "on"}  # Pending actions unlock when the engine stops.


def test_snapshot_priority_tag_on_running_and_queued(tmp_path, monkeypatch):
    from types import SimpleNamespace

    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    tickets = {
        stem: SimpleNamespace(stem=stem, frontmatter=SimpleNamespace(priority=priority, state=state), depends=(), runs_before=(), sections={})
        for stem, priority, state in (("live", "P1", "confirmed"), ("waiting", "P2", "confirmed"), ("blocked", "P0", "draft"))
    }
    merged = tmp_path / "tickets/done/ticket.md"
    merged.parent.mkdir(parents=True)
    merged.write_text("---\npriority: P3\n---\n")
    events = [{"type": "state_transition", "ticket": stem, "body": {"to": state}, "ts": "2026-01-01T00:00:00+00:00"} for stem, state in (("live", "running"), ("done", "merged"))]
    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: (tickets, {}))
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)
    monkeypatch.setattr(watch, "running_stems", lambda *args: ["live"])
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    rows = {r["stem"]: r for r in watch.snapshot(ctx)["rows"]}
    assert {stem: (row["section"], row["priority"], row["priorityTag"]) for stem, row in rows.items()} == {
        "live": ("running", "P1", "P1"),
        "waiting": ("queued", "P2", "P2"),
        "blocked": ("blocked", "P0", ""),
        "done": ("merged", "P3", ""),
    }  # Missing tags, tags on other sections, or using another row's priority differ.


def test_snapshot_badge(tmp_path, monkeypatch):
    from datetime import datetime
    from types import SimpleNamespace

    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)

    def ticket(stem, state="confirmed"):
        return SimpleNamespace(stem=stem, frontmatter=SimpleNamespace(priority="P1", state=state), depends=(), runs_before=(), sections={})

    tickets = {t.stem: t for t in (ticket("live"), ticket("waiting"), ticket("blocked", "draft"))}
    events = [
        {"type": "state_transition", "ticket": "live", "body": {"to": "running"}, "ts": "2026-01-01T00:00:00+00:00"},
        {"type": "state_transition", "ticket": "done", "body": {"to": "merged"}, "ts": "2026-01-01T00:00:00+00:00"},
    ]
    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: (tickets, {}))
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)

    monkeypatch.setattr(watch, "running_stems", lambda *args: ["live"])
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: datetime.fromisoformat("2025-12-31T00:00:00+00:00"))
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    snap = watch.snapshot(ctx)
    assert snap["counts"] == {"blocked": 1, "queued": 1, "running": 1, "merged": 1}  # All four categories must be represented.
    assert snap["badge"] == {"value": 2, "tooltip": "1 running, 1 queued"}  # Merged and blocked rows must not count.
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: None)
    assert watch.snapshot(ctx)["badge"] == {"value": 2, "tooltip": "engine stopped: 1 blocked, 1 queued"}  # Running and merged rows must not count.
    tickets.clear()
    assert watch.snapshot(ctx)["badge"] is None  # Running and merged rows alone must not produce a zero badge.
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: datetime.fromisoformat("2025-12-31T00:00:00+00:00"))
    monkeypatch.setattr(watch, "running_stems", lambda *args: [])
    assert watch.snapshot(ctx)["badge"] is None  # An alive engine with no work must not show zero.


def test_diagnose_prompt_uses_live_running_state(tmp_path, monkeypatch, capsys):
    from chupa.__main__ import main
    from tests.integration.test_config import VALID

    (tmp_path / "config.yaml").write_text(VALID)
    path = tmp_path / "tickets/live/ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text("ticket")
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: [{"type": "state_transition", "ticket": "live", "body": {"to": "running"}, "ts": "2026-01-01T00:00:00+00:00"}])
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: watch.datetime.fromisoformat("2025-12-31T00:00:00+00:00"))
    assert main(["prompt", "diagnose", "live"], cwd=tmp_path) == 0  # The CLI accepts the ticket.
    running = capsys.readouterr().out
    assert main(["prompt", "running", "live"], cwd=tmp_path) == 0
    assert running == capsys.readouterr().out  # Diagnose selects the actual running template.
    monkeypatch.setattr(watch, "lock_holder", lambda state, *args: None)
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
    events = [{"event": "stage_start", "stem": "alpha", "surface": surface, "ts": f"2026-01-01T00:00:0{i}+00:00"} for i, surface in enumerate(("implement", "check", "merge"))]
    (tmp_path / "engine.log").write_text("".join(json.dumps(e) + "\n" for e in events))
    rows = {row["text"]: row for row in watch.snapshot(ctx)["steps"]}
    assert rows["Implement start"]["path"] == "tickets/alpha/run.md"  # The ticket file is a different target.
    assert (rows["Check start"]["kind"], rows["Check start"]["path"]) == ("check_start", "tickets/alpha/checks.json")  # Generic stage kind or ticket path is wrong.
    assert watch.current_step(events, "alpha") == ("Merge", events[-1]["ts"], None)  # A model surface would display model details.
    (directory / "run.md").unlink()
    (directory / "ticket.md").write_text("ticket")
    rows = {row["text"]: row for row in watch.snapshot(ctx)["steps"]}
    assert rows["Implement start"]["path"] == "tickets/alpha/ticket.md"  # A missing run record must not be opened.
    assert watch.current_step([dict(events[1], event="stage_end", outcome="ok")], "alpha")[0] == "Review"  # Check advances to Review.


def test_snapshot_author_steps_open_box_ticket_or_decision(tmp_path, monkeypatch):
    from chupa.box import Box, Resolution
    from chupa.seams import LocalFileSystem

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    box = Box(ctx.state / "box", LocalFileSystem())
    ids = [box.enqueue(message_class="suggestion", origin="operator", summary=summary)[0] for summary in ("First", "Second", "Third")]
    box.resolve(ids[0], Resolution(kind="ticket", link="alpha"))
    box.resolve(ids[1], Resolution(kind="declined", link="declined-box-second"))
    ticket = tmp_path / "tickets/alpha/ticket.md"
    decision = tmp_path / "tickets/decisions/declined-box-second.md"
    for path in (ticket, decision):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("record")
    messages = box.messages()
    events = []
    for i, message in enumerate(messages):
        for event, outcome in (("stage_start", None), ("stage_end", "ok" if i == 0 else "gate_failed")):
            events.append({"event": event, "stem": "author", "surface": "author", "attempt": message.seq, "outcome": outcome, "ts": f"2026-01-01T00:00:0{len(events)}+00:00"})
    events.append({"event": "stage_start", "stem": "author", "surface": "author", "attempt": 99, "ts": "2026-01-01T00:00:06+00:00"})
    (ctx.state / "engine.log").write_text("".join(json.dumps(event) + "\n" for event in events))
    steps = watch.snapshot(ctx)["steps"]
    by_time = {row["ts"]: row for row in steps}
    paths = [str(box.path(message).relative_to(tmp_path)) for message in messages]
    assert [by_time[event["ts"]]["path"] for event in events] == [
        paths[0],
        str(ticket.relative_to(tmp_path)),
        paths[1],
        str(decision.relative_to(tmp_path)),
        paths[2],
        paths[2],
        None,
    ]  # Each attempt and outcome selects its own existing file.
    assert all(row["path"] != "tickets/author/ticket.md" for row in steps)  # The synthetic Author stem is not a ticket.
    assert {row["kind"] for row in steps} == {"author_start", "author_ok", "author_failed"}  # Author has its own icon kind.
    assert all("attempt" not in row and "run_seq" not in row for row in steps)  # Internal lookup data must not reach the extension.
    decision.unlink()
    assert next(row for row in watch.snapshot(ctx)["steps"] if row["ts"] == events[3]["ts"])["path"] == paths[1]  # A missing resolution falls back to its message.


def test_snapshot_triage_and_retro_steps_open_their_files(tmp_path, monkeypatch):
    from chupa.box import Box, Resolution
    from chupa.seams import LocalFileSystem

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    box = Box(ctx.state / "box", LocalFileSystem())
    box.resolve(box.enqueue(message_class="suggestion", origin="operator", summary="First")[0], Resolution(kind="ticket", link="alpha"))
    message = box.messages()[0]
    for path in ("tickets/alpha/ticket.md", "tickets/retro/000007.md"):
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text("record")
    events = [
        {"event": "stage_start", "stem": "triage", "surface": "triage", "attempt": 3, "run_seq": message.seq},
        {"event": "stage_end", "stem": "triage", "surface": "triage", "attempt": 3, "run_seq": message.seq, "outcome": "ok"},
        {"event": "stage_start", "stem": "retro", "surface": "retro", "attempt": 1, "run_seq": 7},
        {"event": "stage_start", "stem": "retro", "surface": "retro", "attempt": 1, "run_seq": 8},
    ]
    events = [dict(e, ts=f"2026-01-01T00:00:0{i}+00:00") for i, e in enumerate(events)]
    (ctx.state / "engine.log").write_text("".join(json.dumps(event) + "\n" for event in events))
    by_time = {row["ts"]: row for row in watch.snapshot(ctx)["steps"]}
    assert [by_time[e["ts"]]["path"] for e in events] == [
        str(box.path(message).relative_to(tmp_path)),
        "tickets/alpha/ticket.md",
        "tickets/retro/000007.md",
        None,
    ]  # Triage keys its message by run_seq; retro opens its report, never tickets/retro/ticket.md.


def test_snapshot_box_messages(tmp_path, monkeypatch):
    from chupa.box import Box, Resolution
    from chupa.seams import LocalFileSystem

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    box = Box(ctx.state / "box", LocalFileSystem())
    first, _ = box.enqueue(message_class="suggestion", origin="operator", summary="First message")
    second, _ = box.enqueue(message_class="failure_report", origin="engine", summary="Second message\nMore detail", stage="check", outcome="failed")
    box.resolve(first, Resolution(kind="ticket", link="fixed"))
    third, _ = box.enqueue(
        message_class="retro_finding",
        origin="retro",
        summary="Slow",
        retro_report_key="retro/1",
        fixed_failure="Slow",
        overcorrection_risk="Coverage",
        test_issue="slow",
        proposed_paths=["tests/unit/test_x.py"],
    )
    snap = watch.snapshot(ctx)
    assert ["Test issue", "slow"] in snap["box"][0]["fields"]
    assert ["Proposed paths", "tests/unit/test_x.py"] in snap["box"][0]["fields"]
    snap["box"].pop(0)
    snap["boxCounts"]["pending"] -= 1
    assert [row["id"] for row in snap["box"]] == [second, first]  # Arrival order would reverse these.
    resolved = snap["box"][1]
    assert (resolved["state"], resolved["status"], resolved["link"]) == ("resolved", "suggestion · author -> fixed", "tickets/fixed/ticket.md")  # Pending or a decision path loses the resolution.
    assert (tmp_path / resolved["path"]).is_file()  # The path must point to the actual message file.
    assert snap["boxCounts"] == {"pending": 1, "author": 1, "tombstone": 0, "declined": 0}  # Counting all messages as pending or omitting resolved authors differs.
    assert snap["box"][0]["fields"] == [["Summary", "Second message\nMore detail"], ["Origin", "engine"], ["Stage", "check: failed"]]  # The summary must retain its second line and stage its outcome.


def test_snapshot_box_external_state_and_resolution_counts(tmp_path, monkeypatch):
    from chupa.box import Box, Resolution, Verdict
    from chupa.seams import LocalFileSystem

    root = tmp_path / "workspace"
    root.mkdir()
    state = tmp_path / "external"
    ctx = watch.Context(root, state, root / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    box = Box(state / "box", LocalFileSystem())
    tomb, _ = box.enqueue(message_class="suggestion", origin="one", summary="A" * 125)
    decision, _ = box.enqueue(message_class="suggestion", origin="two", summary="Decision")
    box.record_verdict(tomb, Verdict(verdict="tombstone", produced_by_spec_version="v1", rationale="covered"))
    box.resolve(tomb, Resolution(kind="tombstone", link="covered"))
    box.resolve(decision, Resolution(kind="declined", link="chosen"))
    snap = watch.snapshot(ctx)
    assert snap["boxCounts"] == {"pending": 0, "author": 0, "tombstone": 1, "declined": 1}  # Resolution kinds must be counted separately.
    assert [row["link"] for row in snap["box"]] == ["tickets/decisions/chosen.md", "tickets/decisions/covered.md"]  # Both records use their own names.
    assert all(row["path"] is None for row in snap["box"])  # External files cannot be opened relative to the workspace.
    assert snap["box"][1]["summary"] == "A" * 117 + "..."  # The status truncation applies only to the row.
    assert ["Recorded verdict", "tombstone: covered"] in snap["box"][1]["fields"]  # A resolution must not hide its recorded verdict.


def test_snapshot_holds_a_parked_ticket(tmp_path, monkeypatch):
    from types import SimpleNamespace

    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    ticket = SimpleNamespace(stem="work", frontmatter=SimpleNamespace(priority="P1", state="confirmed"), depends=(), runs_before=(), sections={})
    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: ({"work": ticket}, {}))
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    for terminal, reason in (("premise_failed", "review"), ("gate_failed", "verification,diff_budget")):
        events = [
            {"type": "state_transition", "ticket": "work", "body": {"to": "running", "ticket_sha": "blob-B"}, "ts": "2026-01-01T00:00:00+00:00"},
            {"type": "state_transition", "ticket": "work", "body": {"to": terminal, "reason": reason}, "ts": "2026-01-01T00:00:01+00:00"},
        ]
        monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)
        for blobs, section, is_held in (({"work": "blob-B"}, "blocked", True), ({"work": "blob-C"}, "queued", False), ({}, "queued", False)):
            monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: blobs)
            row = watch.snapshot(ctx)["rows"][0]
            assert (row["section"], row["held"]) == (section, is_held)  # Matching content alone must hold.
            if is_held:
                assert row["status"] == f"held until the ticket changes (last: {terminal})"  # A generic retry reason hides the hold.


def test_queue_reports_content_hold(tmp_path):
    from types import SimpleNamespace

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    path = tmp_path / "tickets/work/ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nstate: confirmed\npriority: P1\n---\n## Depends on\nnone\n")
    events = [
        {"type": "state_transition", "ticket": "work", "body": {"to": "running", "ticket_sha": "B"}},
        {"type": "state_transition", "ticket": "work", "body": {"to": "premise_failed"}},
    ]
    history = [SimpleNamespace(**e) for e in events]
    holds = watch.held(history, {"work": "B"})
    assert watch.queue(ctx, events, {"work": events[-1]["body"]}, set(), holds) == [("P1", "work", "held until the ticket changes")]  # A retry or ready label conceals the park.


def test_snapshot_reject_queue_uses_configured_caps(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from tests.integration.test_config import VALID

    (tmp_path / "config.yaml").write_text(VALID + "caps: {retry: 1}\n")
    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    tickets = {s: SimpleNamespace(stem=s, frontmatter=SimpleNamespace(priority="P1", state="confirmed"), depends=(), runs_before=(), sections={}) for s in ("retry", "spent")}
    events = [{"type": "state_transition", "ticket": s, "body": {"to": "gate_failed", "routed": "reject_queue"}, "ts": "2026-01-01T00:00:00+00:00"} for s in tickets]
    events.append({"type": "cap_consumed", "ticket": "spent", "body": {"cap": "retry"}, "ts": "2026-01-01T00:00:01+00:00"})
    monkeypatch.setattr(watch, "load_tickets", lambda ctx, skip: (tickets, {}))
    monkeypatch.setattr(watch, "journal", lambda *args, **kwargs: events)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    rows = {r["stem"]: r for r in watch.snapshot(ctx)["rows"]}
    assert (rows["retry"]["section"], rows["retry"]["held"], rows["retry"]["status"]) == ("queued", False, "retry pending (last: gate_failed)")  # Treating all Reject entries as held loses the retry.
    assert (rows["spent"]["section"], rows["spent"]["held"], rows["spent"]["status"]) == ("blocked", True, "held (last: gate_failed)")  # Ignoring the configured retry limit queues spent work.
    for stem in tickets:
        path = tmp_path / "tickets" / stem / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nstate: confirmed\npriority: P1\n---\n## Depends on\nnone\n")
    last = {stem: {"to": "gate_failed"} for stem in tickets}
    projected = {stem: why for _, stem, why in watch.queue(ctx, events, last, set(), set())}
    assert projected == {"retry": "retry pending (last: gate_failed)", "spent": "NEEDS YOUR KEEP OR KILL"}  # Queue explanations must distinguish available and spent caps.


def test_snapshot_watch_uses_configured_state(tmp_path, capsys):
    from pathlib import Path

    from chupa.__main__ import main

    config = tmp_path / "host.yaml"
    config.write_text(Path("config.yaml").read_text().replace("state_dir: .chupa/state", "state_dir: custom-state"))
    assert main(["--config", str(config), "snapshot"]) == 0
    snap = json.loads(capsys.readouterr().out)
    assert snap["watch"] == [
        {"base": str(Path.cwd().resolve()), "glob": "tickets/*/ticket.md"},
        {"base": str((tmp_path / "custom-state").resolve()), "glob": "{journal/*.jsonl,queue.json,engine.log,box/*.json}"},
    ]  # The state watcher must not use the repository base.


def test_requisition_review_steps(tmp_path):
    events = [dict(event=event, stem="alpha", surface="requisition_review", ts=f"2026-01-01T00:00:0{i}+00:00", outcome="gate_failed") for i, event in enumerate(("stage_start", "stage_end"))]
    rows = watch.recent_steps(tmp_path, events, 10)
    assert [(r["text"], r["kind"]) for r in rows] == [("Requisition end (gate_failed)", "requisition_review_failed"), ("Requisition start", "requisition_review_start")]
    assert watch.current_step(events[:1], "alpha") == ("Requisition", events[0]["ts"], "requisition_review")
    assert watch.current_step(events, "alpha") == ("Implement", events[1]["ts"], None)


def test_snapshot_review_owner_without_ticket_has_no_path(tmp_path, monkeypatch):
    ctx = watch.Context(tmp_path, tmp_path, tmp_path / "config.yaml", None, None, None)
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda ctx: (set(), set()))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda ctx: {})
    monkeypatch.setattr(watch, "commits", lambda ctx: {})
    event = {"event": "stage_start", "stem": "review-x", "surface": "requisition_review", "ts": "2026-01-01T00:00:00+00:00"}
    (tmp_path / "engine.log").write_text(json.dumps(event) + "\n")
    row = watch.snapshot(ctx)["steps"][0]
    assert row["stem"] == "review-x"
    assert row["path"] is None  # A nonexistent ticket must not be offered as a link.


def test_recent_steps_phase_events(tmp_path):
    log = [
        {"ts": f"2026-01-01T00:00:0{i}+00:00", **event}
        for i, event in enumerate(
            [
                {"event": "phase_start", "phase": "preflight"},
                {"event": "phase_end", "phase": "preflight", "outcome": "ok"},
                {"event": "phase_end", "phase": "retro_check", "outcome": "no_report"},
                {"event": "phase_end", "phase": "retro_check", "outcome": "failed"},
            ]
        )
    ]
    rows = watch.recent_steps(tmp_path, log, 10)
    assert [(r["text"], r["kind"], r["stem"]) for r in rows] == [
        ("Retro check end (failed)", "retro_check_failed", None),
        ("Retro check end (no report)", "retro_check_ok", None),
        ("Preflight end (ok)", "preflight_ok", None),
        ("Preflight start", "preflight_start", None),
    ]


def test_snapshot_review_locks_for_changed_evidence(tmp_path):
    from chupa.git import Git
    from chupa.lockfile import Lockfile
    from chupa.seams import SubprocessExec
    from tests.integration.test_cli import ENV
    from tests.integration.test_drain import Clock, commit_ticket, confirmed, make_root
    from tests.integration.test_git import commit_lock

    root = make_root(tmp_path)
    commit_ticket(root, "candidate", confirmed())
    evidence = root / "tickets/candidate/evidence/proof.txt"
    evidence.parent.mkdir()
    evidence.write_text("original")
    subprocess.run(["git", "-C", str(root), "add", str(evidence)], env=ENV, check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-m", "evidence"], env=ENV, check=True, capture_output=True)
    evidence.write_text("changed")
    state = root / ".chupa/state"
    git = Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(state))
    ctx = watch.Context(root, state, root / "config.yaml", SubprocessExec(), git, ENV)
    lock = Lockfile(state, verb="drain", instance_id="test", clock=Clock())
    lock.acquire()
    try:
        row = next(row for row in watch.snapshot(ctx)["rows"] if row["stem"] == "candidate")
        assert row["committed"] is True
        assert row["menu"]["chupaReview"] == "on"
    finally:
        lock.release()


def test_snapshot_commit_lock_display(tmp_path, monkeypatch):
    from types import SimpleNamespace

    ctx = watch.Context(tmp_path, tmp_path / "state", tmp_path / "config.yaml", None, None, None)
    ctx.state.mkdir()
    monkeypatch.setattr(watch, "load_tickets", lambda *args: ({}, {}))
    monkeypatch.setattr(watch, "committed_ticket_shas", lambda *args: {})
    monkeypatch.setattr(watch, "uncommitted_tickets", lambda *args: (set(), set()))
    monkeypatch.setattr(watch, "commits", lambda *args: {})
    assert watch.snapshot(ctx)["commitLock"] == ""
    path = ctx.state / "commit.lock"
    path.write_text("")
    assert watch.snapshot(ctx)["commitLock"] == ""
    started = "2026-01-01T00:00:00+00:00"
    path.write_text(json.dumps({"pid": os.getpid(), "started_at": started}))
    original = watch.Path.read_bytes
    monkeypatch.setattr(watch.Path, "read_bytes", lambda self: b"python\0-m\0chupa\0review\0stem\0" if str(self) == f"/proc/{os.getpid()}/cmdline" else original(self))
    assert watch.snapshot(ctx)["commitLock"] == f"review since {watch.clock(started)} (pid {os.getpid()})"


def test_draft_assessment_menu_tracks_snapshot_draft(tmp_path):
    from chupa import observe
    from chupa.git import Git
    from chupa.seams import SubprocessExec
    from tests.integration.test_cli import ENV, git_out
    from tests.integration.test_drain import confirmed, make_root
    from tests.integration.test_git import commit_lock

    root = make_root(tmp_path)
    for stem, state in (("committed-draft", "draft"), ("confirmed-ticket", "confirmed"), ("untracked-draft", "draft")):
        path = root / "tickets" / stem / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(confirmed().replace("state: confirmed", f"state: {state}"))
        if stem != "untracked-draft":
            git_out(root, "add", str(path.relative_to(root)))
    git_out(root, "commit", "-m", "tickets")
    state = root / ".chupa/state"
    git = Git(SubprocessExec(), env=ENV, timeout=30, commit_lock=commit_lock(state))
    ctx = observe.Context(root, state, root / "config.yaml", SubprocessExec(), git, ENV)
    rows = {row["stem"]: row for row in observe.snapshot(ctx)["rows"]}
    assert {stem: rows[stem]["menu"]["chupaAskDrafts"] for stem in ("committed-draft", "untracked-draft", "confirmed-ticket")} == {
        "committed-draft": "on",
        "untracked-draft": "off",
        "confirmed-ticket": "off",
    }  # Raw frontmatter and always-on menus differ.
