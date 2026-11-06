import json
import os
import subprocess
import sys

import watch


def test_queue_projection_and_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(watch, "ROOT", tmp_path)
    (tmp_path / "config.yaml").write_text("state_dir: state\n")
    for stem, priority, dependency in [("old", "P1", "none"), ("new", "P2", "none"), ("blocked", "P0", "missing")]:
        path = tmp_path / "tickets" / stem / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\nstate: confirmed\npriority: {priority}\n---\n## Depends on\n- {dependency}\n")
    # The real format uses plain 'none', not a dependency named none.
    for stem in ("old", "new"):
        path = tmp_path / "tickets" / stem / "ticket.md"
        path.write_text(path.read_text().replace("- none", "none"))
    assert [row[1] for row in watch.queue([], {}, set())] == ["blocked", "old", "new"]
    (tmp_path / "state").mkdir()
    (tmp_path / "state/queue.json").write_text(json.dumps({"at": "2026-01-01T00:00:00+00:00", "order": ["new", "old"], "runs_before": {"new": ["old"]}}))
    assert watch.queue([], {}, set()) == [
        ("P2", "new", "ready, not run yet; runs before: old"),
        ("P1", "old", "ready, not run yet"),
        ("P0", "blocked", "waits on missing"),
    ]


def test_drain_processes_only_this_repo(tmp_path, monkeypatch):
    # Another host's drain runs from this venv with its own --config; only this checkout's drains count.
    monkeypatch.setattr(watch, "ROOT", tmp_path)
    monkeypatch.setattr(watch.os, "readlink", lambda path: str(tmp_path))
    monkeypatch.setattr(watch, "started", lambda pid: pid)
    rows = [
        (30, 1, "/v/bin/python3 -m chupa --config config.yaml drain"),
        (10, 1, "/v/bin/python3 -m chupa drain"),
        (20, 1, "/v/bin/python3 -m chupa --config /elsewhere/config.yaml drain"),
        (40, 1, "/v/bin/python3 -m chupa serve"),
    ]
    assert watch.drain_processes(rows) == [10, 30]


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

    monkeypatch.setattr(watch, "ROOT", tmp_path)
    (tmp_path / "config.yaml").write_text("state_dir: state\n")
    path = tmp_path / "tickets" / "child" / "ticket.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nstate: confirmed\npriority: P1\n---\n## Depends on\n- parent\n")
    events = [
        {"type": "state_transition", "ticket": "parent", "body": {"to": "rejected"}, "ts": "2026-01-01T00:00:00+00:00"},
        {"type": "signal", "ticket": "parent", "body": {"signal": SUPERSEDES, "successors": ["part"]}, "ts": "2026-01-01T00:00:01+00:00"},
        {"type": "state_transition", "ticket": "part", "body": {"to": "merged"}, "ts": "2026-01-01T00:00:02+00:00"},
    ]
    last_state = {e["ticket"]: e["body"] for e in events if e["type"] == "state_transition"}
    assert watch.queue(events, last_state, set()) == [("P1", "child", "ready, not run yet")]
