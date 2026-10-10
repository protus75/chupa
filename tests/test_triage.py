"""Production CLI composition with a scripted provider and a real ticket-plane checkout."""

import json
from pathlib import Path

import pytest

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


def test_report_ingested_before_pending_scan(tmp_path, monkeypatch):
    from tests.test_inbox import arrival
    from chupa import inbox

    root, box = root_with_box(tmp_path)
    source = arrival(root)
    replay = root / "replay.json"
    data = replay.read_bytes()
    replay.write_bytes(data + b" " * (1024 * 1024 - len(data)))
    config = root / "config.yaml"
    config.write_text(config.read_text() + "report_inbox: inbox\n")
    assert box.pending() == []
    def classify(request):
        message, = box.pending()
        assert message.report is not None and message.has_repro
        assert "structured log" in request.rendered and 'initial_state' in request.rendered
        assert "excerpt truncated" in request.rendered
        assert (box.root / message.report.custody.replay).read_bytes() == replay.read_bytes()
        return reply("decision")
    llm = FakeLLM([classify])
    assert run(root, monkeypatch, llm) == 0
    assert len(llm.requests) == 1 and box.pending() == []
    assert source.exists()
    config.write_text(config.read_text().replace("report_inbox: inbox\n", ""))
    def forbidden(path):
        pytest.fail("absent report inbox must not read report sources")
    monkeypatch.setattr(inbox, "validate_report", forbidden)
    assert run(root, monkeypatch, FakeLLM([])) == 0


def test_report_author_failure_is_decision(tmp_path, monkeypatch):
    from tests.test_inbox import arrival
    root, box = root_with_box(tmp_path)
    arrival(root)
    config = root / "config.yaml"
    config.write_text(config.read_text() + "report_inbox: inbox\n")
    llm = FakeLLM([reply("author"), *[json.dumps({"stem": "broken", "ticket": "bad"})] * 7])
    assert run(root, monkeypatch, llm) == 0
    message, = box.messages()
    assert message.resolution == Resolution(kind="decision", link=f"decision-{message.id}")
    assert len([e for e in events(root) if e.body.get("signal") == "author_invoked"]) == 1
    assert len([r for r in llm.requests if r.surface == "author"]) == 7
    assert not (root / "tickets/broken").exists()
    assert "tickets/broken" not in git_out(root, "status", "--porcelain")
    assert run(root, monkeypatch, FakeLLM([])) == 0
    # A later arrival has its own allowance and can reuse the rejected stem.
    from tests.test_author import bug_reply
    source = root / "inbox/a.json"
    source.rename(source.with_name("b.json"))
    assert run(root, monkeypatch, FakeLLM([reply("author"), bug_reply("broken"),
                                          requisition_reply("approve")])) == 0
    assert (root / "tickets/broken/ticket.md").is_file()


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


@pytest.mark.parametrize(("recorded_verdict", "tombstone_link"), [
    (True, None), (False, "own-record"), (False, "known"),
])
def test_reopened_message_bypasses_its_tombstone(tmp_path, monkeypatch, recorded_verdict, tombstone_link):
    from chupa import triage
    from chupa.box import RereportJournal
    root, source = root_with_box(tmp_path)
    box = Box(source.root, source.fs, rereport=RereportJournal(Journal(root / ".chupa/state", Clock())))
    commit_ticket(root, "known", confirmed())
    id = enqueue(box, "reopened concern")
    assert run(root, monkeypatch, FakeLLM([reply("tombstone", link="known")])) == 0
    path = root / record_path(f"tombstone-{id}")
    before = path.read_bytes()
    head = git_out(root, "rev-parse", "HEAD").strip()
    commits = subjects(root)
    for n in range(3):
        box.record_rereport(id, occurrence_id=f"distinct/{n}")
    assert box.get(id).reopen and box.get(id).verdict is None
    script = [author_reply("reconsidered"), requisition_reply("approve")]
    if recorded_verdict:
        box.record_verdict(id, Verdict(verdict="author", produced_by_spec_version="1.0", rationale="new evidence"))
    else:
        def classify(request):
            assert f"tombstone-{id}: tombstone" not in request.rendered
            assert '"reopen": true' in request.rendered
            return reply("tombstone", link=f"tombstone-{id}" if tombstone_link == "own-record" else tombstone_link)
        script.insert(0, classify)
    author = triage.author
    calls = []
    async def author_with_preserved_registry(*args):
        assert path.read_bytes() == before
        assert git_out(root, "rev-parse", "HEAD").strip() == head
        assert git_out(root, "show", f"HEAD:{record_path(f'tombstone-{id}')}").encode() == before
        calls.append(id)
        return await author(*args)
    monkeypatch.setattr(triage, "author", author_with_preserved_registry)
    llm = FakeLLM(script)
    assert run(root, monkeypatch, llm) == 0
    assert calls == [id]
    assert box.get(id).resolution == Resolution(kind="ticket", link="reconsidered")
    assert path.read_bytes() == before
    assert git_out(root, "show", f"HEAD:{record_path(f'tombstone-{id}')}").encode() == before
    assert subjects(root) == ["chupa(reconsidered): ticket", *commits]
    assert (root / "tickets/reconsidered/ticket.md").is_file()
    count = len(llm.requests)
    assert run(root, monkeypatch, llm) == 0 and len(llm.requests) == count
