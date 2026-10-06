import asyncio
import hashlib
import json
import os
from pathlib import Path

import pytest

from chupa.box import (
    BOOTSTRAP_ORIGIN, Box, BoxError, DecisionRecord, Message, Resolution, Verdict,
    ingest_bootstrap, ingest_main_checkout, normalize, parse_record, read_registry,
    record_path, render_record, signature,
)
from chupa.git import Git
from chupa.seams import LocalFileSystem, SubprocessExec


def test_signature_recipe():
    assert normalize(" a 42 b ") == normalize("a b") == "a b"
    assert normalize(" 42 /tmp/42 a 37 b ") == "a b"
    assert signature("failure_report", "stem", "check", "red", reason="line 42 /tmp/a failed") == signature(
        "failure_report", "stem", "check", "red", reason="line 51 /other/b failed"
    )
    assert signature("x", reason="line 42 failed") == signature("x", reason="line failed")
    base = signature("failure_report", "stem", "check", "red", reason="failed")
    for fields in [
        ("suggestion", "stem", "check", "red"), ("failure_report", "other", "check", "red"),
        ("failure_report", "stem", "review", "red"), ("failure_report", "stem", "check", "ok"),
    ]:
        assert signature(*fields, reason="failed") != base
    line = "line 42 /tmp/a failed"
    compact = json.dumps(["suggestion", BOOTSTRAP_ORIGIN, normalize(line)], separators=(",", ":"))
    assert signature("suggestion", BOOTSTRAP_ORIGIN, reason=line) == hashlib.sha256(compact.encode()).hexdigest()


def test_enqueue_dedup_and_validation(tmp_path):
    box = Box(tmp_path / "box", LocalFileSystem())
    first, created = box.enqueue(message_class="suggestion", origin="one", summary="hello")
    assert created
    message = box.get(first)
    assert first == f"box-000001-{message.signature[:8]}"
    assert [p.name for p in box.root.glob("*.json")] == [f"000001-{message.signature[:8]}.json"]
    assert Message.model_validate_json(next(box.root.glob("*.json")).read_text()) == message
    assert box.enqueue(message_class="suggestion", origin="one", summary="hello") == (first, False)
    assert len(list(box.root.glob("*.json"))) == 1
    second, created = box.enqueue(message_class="suggestion", origin="two", summary="hello")
    assert created and box.get(second).seq == 2
    box.resolve(first, Resolution(kind="ticket", link="ticket-a"))
    assert box.enqueue(message_class="suggestion", origin="one", summary="hello") == (first, False)
    assert len(list(box.root.glob("*.json"))) == 2
    for kwargs in [
        {"message_class": "bug_report", "origin": "x", "summary": "bug"},
        {"message_class": "suggestion", "origin": "x", "summary": "text", "bug_origin": "player", "has_repro": True},
        {"message_class": "suggestion", "origin": "x", "summary": "text", "stage": "check"},
    ]:
        with pytest.raises(BoxError):
            box.enqueue(**kwargs)
    assert len(list(box.root.glob("*.json"))) == 2


def test_durability_and_corruption(tmp_path):
    box = Box(tmp_path / "box", LocalFileSystem())
    id, _ = box.enqueue(message_class="bug_report", origin="host", summary="crash", bug_origin="player", has_repro=True)
    verdict = Verdict(verdict="author", produced_by_spec_version="1", rationale="repro exists")
    box.record_verdict(id, verdict)
    assert box.pending()[0].verdict == verdict
    resolution = Resolution(kind="ticket", link="crash-fix")
    box.resolve(id, resolution)
    assert Box(box.root, LocalFileSystem()).get(id).resolution == resolution
    assert box.pending() == []
    with pytest.raises(BoxError, match=id):
        box.resolve(id, resolution)
    (box.root / "bad.json").write_text("{}")
    with pytest.raises(BoxError, match="bad.json"):
        box.messages()


def test_registry_format(tmp_path):
    record = DecisionRecord(id="b", kind="decision", link="ticket-b", reopen_after_days=30)
    assert record_path("b") == Path("tickets/decisions/b.md")
    assert parse_record(render_record(record, "Reason\n")) == (record, "Reason\n")
    for text in [
        "body only", "---\nid: b\nkind: decision\nlink: ticket-b\n---\nbody",
        "---\nid: b\nkind: decision\nlink: ticket-b\nreopen_after_days: 30\nextra: x\n---\nbody",
    ]:
        with pytest.raises(BoxError):
            parse_record(text)
    folder = tmp_path / "tickets" / "decisions"
    folder.mkdir(parents=True)
    (folder / "b.md").write_text(render_record(record, "B"))
    (folder / "a.md").write_text(render_record(DecisionRecord(id="a", kind="tombstone", link="b", reopen_after_days=7), "A"))
    assert [item[0].id for item in read_registry(tmp_path)] == ["a", "b"]


def test_bootstrap_ingest_uses_main_checkout(tmp_path):
    main = tmp_path / "main"
    linked = tmp_path / "linked"
    main.mkdir()
    (main / "config.yaml").write_text(
        "schema_version: 1\nstate_dir: .chupa\nproviders:\n"
        "  - {name: test, kind: cli, package: test-cli, models_by_tier: {low: a, medium: b, high: c, max: d}, limits: {concurrency: 1}}\n"
        "routing:\n  - {tier: medium, surface: implement, candidates: [{provider: test}]}\n"
        "review: {}\nmerge: {}\nengine_plane_safety_inventory: []\n"
    )
    source = main / "bootstrap" / "suggestions.md"
    source.parent.mkdir()
    source.write_text("  first line  \n\n second line\n")
    env = {
        **os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
    }
    git = Git(SubprocessExec(), env=env, timeout=30.0)
    fs = LocalFileSystem()

    async def scenario():
        await git.init(main, branch="main")
        await git.add(main, ["config.yaml", "bootstrap/suggestions.md"])
        await git.commit(main, "base")
        await git.worktree_add(main, linked, "linked", "main")
        (linked / "bootstrap" / "suggestions.md").unlink()
        assert await ingest_main_checkout(linked, git, fs) == 2
        assert await ingest_main_checkout(linked, git, fs) == 0
        source.unlink()
        assert await ingest_main_checkout(linked, git, fs) == 0

    asyncio.run(scenario())
    box = Box(main / ".chupa" / "box", fs)
    assert [(m.message_class, m.origin, m.summary) for m in box.messages()] == [
        ("suggestion", BOOTSTRAP_ORIGIN, "first line"),
        ("suggestion", BOOTSTRAP_ORIGIN, "second line"),
    ]
    assert not (linked / ".chupa").exists()
    assert ingest_bootstrap(box, "first line\nsecond line\n") == [m.id for m in box.messages()]
