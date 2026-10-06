"""Production CLI composition with a scripted provider and a real ticket-plane checkout."""

import json
from pathlib import Path

from chupa.__main__ import main
from chupa.box import Box, DecisionRecord, Resolution, Verdict, parse_record, record_path, render_record
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.lockfile import Lockfile
from chupa.seams import LocalFileSystem
from tests.test_cli import ENV, git_out
from tests.test_drain import Clock, commit_ticket, confirmed, make_root


def root_with_box(tmp_path: Path) -> tuple[Path, Box]:
    root = make_root(tmp_path)
    config = root.joinpath("config.yaml")
    config.write_text(config.read_text().replace("  - {tier: medium, surface: implement, candidates: [{provider: claude}]}", """  - {tier: medium, surface: implement, candidates: [{provider: claude}]}
  - {tier: low, surface: author, candidates: [{provider: claude}]}
  - {tier: medium, surface: author, candidates: [{provider: claude}]}
  - {tier: high, surface: author, candidates: [{provider: claude}]}
  - {tier: max, surface: author, candidates: [{provider: claude}]}
  - {tier: low, surface: review, candidates: [{provider: claude}]}
  - {tier: medium, surface: review, candidates: [{provider: claude}]}
  - {tier: high, surface: review, candidates: [{provider: claude}]}
  - {tier: max, surface: review, candidates: [{provider: claude}]}
"""))
    return root, Box(root / ".chupa" / "state" / "box", LocalFileSystem())


def enqueue(box: Box, summary: str) -> str:
    return box.enqueue(message_class="suggestion", origin="test", summary=summary)[0]


def reply(verdict: str, *, link=None, summary="Triage's own summary", evidence=None, days=30) -> str:
    return json.dumps({"verdict": verdict, "link": link, "summary": summary,
                       "rationale": "Observed and classified", "evidence": evidence or [],
                       "reopen_after_days": None if verdict == "author" else days})


def author_reply(stem: str) -> str:
    return json.dumps({"stem": stem, "ticket": """---
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/thing.py

## Goal / Why
`chupa/thing.py` is repaired.

## Scope in / Scope out
- In: `chupa/thing.py`.
- Out: unrelated files.

## Scope fence
- chupa/thing.py

## Acceptance criteria
- `uv run pytest` exits 0.

## Verification
```
uv run pytest
```

## Definition of rejected
- `chupa/thing.py` cannot be changed safely.

## Time budget
- expected: 10m
- stuck: 20m
"""})


def requisition_reply(verdict: str, findings: list | None = None) -> str:
    return json.dumps({"verdict": verdict, "summary": "reviewed", "findings": findings or []})


def run(root: Path, monkeypatch, llm: FakeLLM) -> int:
    monkeypatch.setattr("chupa.__main__.ProviderLLM", lambda *args, **kwargs: llm)
    return main(["triage"], cwd=root, env=ENV, clock=Clock())


def subjects(root: Path) -> list[str]:
    return git_out(root, "log", "--format=%s").splitlines()


def events(root: Path):
    return Journal(root / ".chupa" / "state", Clock()).read()


def test_three_verdicts_and_second_pass_and_stale_author(tmp_path, monkeypatch, capsys):
    root, box = root_with_box(tmp_path)
    commit_ticket(root, "existing", confirmed())
    marker = "RAW-SUMMARY-UNIQUE-987"
    ids = [enqueue(box, marker), enqueue(box, "another concern"), enqueue(box, "third concern")]
    messages = [box.get(id) for id in ids]
    llm = FakeLLM([reply("tombstone", link="existing", days=7), reply("decision", days=14),
                   reply("author"), author_reply("authored"), requisition_reply("approve")])
    before = subjects(root)
    assert run(root, monkeypatch, llm) == 0
    assert "ticket -> authored" in capsys.readouterr().out
    assert subjects(root)[:3] == ["chupa(authored): ticket", f"chupa(decisions): decision-{ids[1]}",
                                   f"chupa(decisions): tombstone-{ids[0]}"]
    assert subjects(root)[3:] == before
    for id, kind, link, days in [(ids[0], "tombstone", "existing", 7),
                                 (ids[1], "decision", ids[1], 14)]:
        path = record_path(f"{kind}-{id}")
        record, body = parse_record((root / path).read_text())
        assert (record.kind, record.link, record.reopen_after_days) == (kind, link, days)
        assert marker not in body
        assert box.get(id).status == "resolved"
        assert git_out(root, "rev-parse", f"HEAD:{path}").strip()
    assert box.get(ids[2]).resolution == Resolution(kind="ticket", link="authored")
    assert box.get(ids[2]).verdict.produced_by_spec_version == "1.0"
    assert len(llm.requests) == 5
    assert [(r.surface, r.tier, r.ticket) for r in llm.requests] == [
        ("triage", "medium", None), ("triage", "medium", None), ("triage", "medium", None),
        ("author", "medium", None), ("requisition_review", "medium", None),
    ]
    keys = {e.key for e in events(root) if e.type == EventType.EFFECT_COMPLETION and e.key.startswith("llm/")}
    assert keys == {f"llm/triage/{m.seq}/triage/0/1" for m in messages} | {
        f"llm/author/0/author/{messages[2].seq}/1",
        f"llm/author/0/requisition_review/{messages[2].seq}/1"}
    for m in messages:
        spool = root / ".chupa" / "state" / "spools" / "triage" / str(m.seq) / "0" / "triage" / "call-01"
        assert (spool / "prompt.md").exists() and (spool / "output.txt").exists()
    stale_id = enqueue(box, "stale concern")
    box.record_verdict(stale_id, Verdict(verdict="author", produced_by_spec_version="0.9", rationale="old"))
    assert run(root, monkeypatch, llm) == 0
    assert len(llm.requests) == 5
    assert box.get(stale_id).status == "resolved"
    assert subjects(root)[0] == f"chupa(decisions): decision-{stale_id}"
    stale, body = parse_record((root / record_path(f"decision-{stale_id}")).read_text())
    assert stale.kind == "decision" and "0.9" in body and "1.0" in body


def test_bad_tombstone_link_becomes_decision(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    id = enqueue(box, "bad reference")
    llm = FakeLLM([reply("tombstone", link="missing")])
    assert run(root, monkeypatch, llm) == 0
    record, body = parse_record((root / record_path(f"decision-{id}")).read_text())
    assert record.kind == "decision" and record.link == id and "missing" in body
    assert box.get(id).status == "resolved"


def test_model_echo_of_raw_summary_is_removed_from_record(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    marker = "RAW-SUMMARY-PRIVATE-123"
    id = enqueue(box, marker)
    llm = FakeLLM([reply("decision", summary=marker, evidence=[f"report said {marker}"])])
    assert run(root, monkeypatch, llm) == 0
    committed = git_out(root, "show", f"HEAD:{record_path(f'decision-{id}')}")
    assert marker not in committed


def test_precommitted_record_resolves_without_call(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    id = enqueue(box, "already classified")
    path = record_path(f"decision-{id}")
    (root / path).parent.mkdir(parents=True)
    (root / path).write_text(render_record(DecisionRecord(id=f"decision-{id}", kind="decision",
                                                       link=id, reopen_after_days=8), "Prior classification\n"))
    git_out(root, "add", str(path))
    git_out(root, "commit", "-m", f"chupa(decisions): decision-{id}", "--only", "--", str(path))
    llm = FakeLLM([])
    assert run(root, monkeypatch, llm) == 0
    assert box.get(id).resolution == Resolution(kind="decision", link=f"decision-{id}")
    assert llm.requests == []


def test_uncommitted_record_is_committed_before_resolution(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    id = enqueue(box, "crash after write")
    path = record_path(f"decision-{id}")
    (root / path).parent.mkdir(parents=True)
    (root / path).write_text(render_record(DecisionRecord(id=f"decision-{id}", kind="decision",
                                                       link=id, reopen_after_days=8), "Recover me\n"))
    llm = FakeLLM([])
    assert run(root, monkeypatch, llm) == 0
    assert llm.requests == []
    assert subjects(root)[0] == f"chupa(decisions): decision-{id}"
    assert git_out(root, "rev-parse", f"HEAD:{path}").strip()
    assert box.get(id).status == "resolved"


def test_uncommitted_registry_target_is_not_valid_tombstone_link(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    id = enqueue(box, "new concern")
    target = "decision-other"
    path = record_path(target)
    (root / path).parent.mkdir(parents=True)
    (root / path).write_text(render_record(DecisionRecord(id=target, kind="decision", link="other",
                                                       reopen_after_days=8), "Uncommitted\n"))
    llm = FakeLLM([reply("tombstone", link=target)])
    assert run(root, monkeypatch, llm) == 0
    assert parse_record((root / record_path(f"decision-{id}")).read_text())[0].kind == "decision"
    assert box.get(id).status == "resolved"


def test_invalid_replies_leave_pending_without_commit(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    id = enqueue(box, "invalid reply")
    before = subjects(root)
    llm = FakeLLM(["{}"] * 7)
    assert run(root, monkeypatch, llm) == 0
    assert box.get(id).status == "pending" and box.get(id).verdict is None
    assert subjects(root) == before
    assert len(llm.requests) == 7


def test_lock_contention_exits_two_without_pass(tmp_path, monkeypatch):
    root, box = root_with_box(tmp_path)
    enqueue(box, "locked")
    holder = Lockfile(root / ".chupa" / "state", instance_id="other", clock=Clock())
    holder.acquire()
    llm = FakeLLM([])
    try:
        assert run(root, monkeypatch, llm) == 2
    finally:
        holder.release()
    assert llm.requests == []
    assert not any(e.type == EventType.SIGNAL and e.body.get("signal") == "triage_pass" for e in events(root))
