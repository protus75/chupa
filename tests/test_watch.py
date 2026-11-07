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
        (None, "drain stopped (quiescent)"),
        ("alpha", "Implement end (ok)"),
        ("alpha", "Implement start"),
        (None, "drain started (pid 41)"),
    ]
    assert [r["ts"] for r in rows] == sorted((r["ts"] for r in rows), reverse=True)
    lines = watch.text_snapshot(ctx).split("Recent steps:\n", 1)[1].splitlines()
    assert lines == [f"  {watch.clock(r['ts'])}  " + (f"{r['stem']}  " if r["stem"] else "") + r["text"] for r in rows]
    monkeypatch.setattr(watch, "lock_holder", lambda state: object())
    assert len(watch.recent_steps(state, log, 20)) == 5


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
