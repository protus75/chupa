import json

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
    assert [row[1] for row in watch.queue([], {})] == ["blocked", "old", "new"]
    (tmp_path / "state").mkdir()
    (tmp_path / "state/queue.json").write_text(json.dumps({"at": "2026-01-01T00:00:00+00:00", "order": ["new", "old"], "runs_before": {"new": ["old"]}}))
    assert watch.queue([], {}) == [
        ("P2", "new", "ready, not run yet; runs before: old"),
        ("P1", "old", "ready, not run yet"),
        ("P0", "blocked", "waits on missing"),
    ]
