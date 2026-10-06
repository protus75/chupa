"""Author integration: triage drives the one ticket-plane authoring path."""

import json

from chupa.box import Box, Resolution, Verdict, parse_record, record_path
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.seams import LocalFileSystem
from chupa.tickets import validate_ticket
from tests.test_cli import ENV, git_out
from tests.test_drain import Clock, commit_ticket, confirmed, make_root
from tests.test_triage import author_reply, reply
from chupa.__main__ import main


def _run(root, monkeypatch, llm):
    monkeypatch.setattr("chupa.__main__.ProviderLLM", lambda *args, **kwargs: llm)
    return main(["triage"], cwd=root, env=ENV, clock=Clock())


def _routes(root):
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


def _box(root):
    return Box(root / ".chupa" / "state" / "box", LocalFileSystem())


def _events(root):
    return Journal(root / ".chupa" / "state", Clock()).read()


def _failure(box):
    return box.enqueue(message_class="failure_report", origin="test", summary="current broken behavior",
                       stage="check", outcome="gate_failed")[0]


def test_triage_authors_ticket_and_journals_intake(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    message_id = _failure(box)
    message = box.get(message_id)
    llm = FakeLLM([reply("author"), author_reply("repair-thing")])
    before = git_out(root, "log", "--format=%s").splitlines()
    assert _run(root, monkeypatch, llm) == 0
    text = (root / "tickets/repair-thing/ticket.md").read_text()
    ticket = validate_ticket("repair-thing", text, root)
    assert ticket.frontmatter.source == "box:failure_report" and ticket.frontmatter.state == "draft"
    subjects = git_out(root, "log", "--format=%s").splitlines()
    assert subjects == ["chupa(repair-thing): ticket", *before]
    signals = [e for e in _events(root) if e.type == EventType.SIGNAL and e.ticket == "repair-thing"
               and e.body.get("signal") == "ticket_intake"]
    assert len(signals) == 1
    assert box.get(message_id).resolution == Resolution(kind="ticket", link="repair-thing")
    keys = [e.key for e in _events(root) if e.type == EventType.EFFECT_COMPLETION]
    assert f"llm/author/0/author/{message.seq}/1" in keys
    assert llm.requests[1].tier == "medium"


def test_author_reprompts_for_reused_stem_and_invalid_ticket(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    commit_ticket(root, "existing", confirmed())
    box = _box(root)
    _failure(box)
    invalid = json.dumps({"stem": "bad-ticket", "ticket": "not a ticket"})
    llm = FakeLLM([reply("author"), author_reply("existing"), invalid, author_reply("fresh-ticket")])
    assert _run(root, monkeypatch, llm) == 0
    prompts = [r.rendered for r in llm.requests if r.surface == "author"]
    assert len(prompts) == 3
    assert "already exists" in prompts[1]
    assert "ticket.md has no frontmatter" in prompts[2]
    assert (root / "tickets/fresh-ticket/ticket.md").exists()


def test_author_exhaustion_records_one_decision(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    message_id = _failure(box)
    llm = FakeLLM([reply("author"), *[json.dumps({"stem": "bad", "ticket": "bad"}) for _ in range(7)]])
    assert _run(root, monkeypatch, llm) == 0
    assert not (root / "tickets/bad").exists()
    record, _ = parse_record((root / record_path(f"decision-{message_id}")).read_text())
    assert record.id == f"decision-{message_id}"
    assert box.get(message_id).resolution == Resolution(kind="decision", link=record.id)


def test_prior_author_invocation_records_decision_without_author_call(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    message_id = _failure(box)
    box.record_verdict(message_id, Verdict(verdict="author", produced_by_spec_version="1.0", rationale="broken"))
    Journal(root / ".chupa" / "state", Clock()).append(EventType.SIGNAL,
                                                          {"signal": "author_invoked", "message": message_id})
    llm = FakeLLM([])
    assert _run(root, monkeypatch, llm) == 0
    assert [r for r in llm.requests if r.surface == "author"] == []
    record, _ = parse_record((root / record_path(f"decision-{message_id}")).read_text())
    assert box.get(message_id).resolution == Resolution(kind="decision", link=record.id)
