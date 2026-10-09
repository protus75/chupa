"""Author integration: triage drives the one ticket-plane authoring path."""

import json

import pytest

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


def requisition_reply(verdict, findings=None):
    return json.dumps({"verdict": verdict, "summary": "reviewed", "findings": findings or []})


SNAG = {"code": "scope", "message": "missing test", "paved_road": "add the test", "kind": "authoring_error"}
RMA = {"code": "scope", "message": "plan cannot support this", "paved_road": "repair the plan", "kind": "spec_gap"}


def test_triage_authors_ticket_and_journals_intake(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    message_id = _failure(box)
    message = box.get(message_id)
    llm = FakeLLM([reply("author"), author_reply("repair-thing"), requisition_reply("approve")])
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
    assert f"llm/author/0/requisition_review/{message.seq}/1" in keys
    assert llm.requests[1].tier == "medium"
    verdicts = [e for e in _events(root) if e.type == EventType.SIGNAL
                and e.ticket == "repair-thing" and e.body.get("signal") == "requisition_verdict"]
    assert len(verdicts) == 1 and verdicts[0].body["verdict"] == "approve"


def test_author_reprompts_for_reused_stem_and_invalid_ticket(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    commit_ticket(root, "existing", confirmed())
    box = _box(root)
    _failure(box)
    invalid = json.dumps({"stem": "bad-ticket", "ticket": "not a ticket"})
    llm = FakeLLM([reply("author"), author_reply("existing"), invalid, author_reply("fresh-ticket"),
                   requisition_reply("approve")])
    assert _run(root, monkeypatch, llm) == 0
    prompts = [r.rendered for r in llm.requests if r.surface == "author"]
    assert len(prompts) == 3
    assert "already exists" in prompts[1]
    assert "ticket.md has no frontmatter" in prompts[2]
    assert (root / "tickets/fresh-ticket/ticket.md").exists()


def test_author_snag_reprompts_then_approve(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    _failure(box)
    llm = FakeLLM([reply("author"), author_reply("first"), requisition_reply("snag", [SNAG]),
                   author_reply("second"), requisition_reply("approve")])
    assert _run(root, monkeypatch, llm) == 0
    assert (root / "tickets/second/ticket.md").exists()
    authors = [request for request in llm.requests if request.surface == "author"]
    assert len(authors) == 2 and "- scope: missing test (do instead: add the test)" in authors[1].rendered


def test_author_rma_writes_decision_without_ticket(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    message_id = _failure(box)
    llm = FakeLLM([reply("author"), author_reply("blocked"), requisition_reply("rma", [RMA])])
    assert _run(root, monkeypatch, llm) == 0
    assert not (root / "tickets/blocked").exists()
    assert [request.surface for request in llm.requests] == ["triage", "author", "requisition_review"]
    _, body = parse_record((root / record_path(f"decision-{message_id}")).read_text())
    assert "plan cannot support this" in body


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


def test_reopened_retro_ticket_starts_draft(tmp_path, monkeypatch):
    from chupa.box import RereportJournal
    from chupa.config import load_config
    from chupa.policy import baseline_identity
    from tests.test_retro_box import PROPOSAL
    root = make_root(tmp_path)
    _routes(root)
    path = root / "config.yaml"
    path.write_text(path.read_text().replace("engine_plane_safety_inventory: []", "engine_plane_safety_inventory: [config.yaml]"))
    cfg = load_config(None, cwd=root)
    journal = Journal(cfg.state_dir, Clock())
    journal.append(EventType.SIGNAL, {"signal": "review_baseline", "verdict": "GO", "identity": baseline_identity(cfg)})
    assert cfg.box_policy["retro_finding"] == "confirmed" and cfg.engine_plane_safety_inventory
    box = Box(cfg.state_dir / "box", LocalFileSystem(), rereport=RereportJournal(journal))
    id, _ = box.enqueue(message_class="retro_finding", origin="retro", summary=PROPOSAL["fixed_failure"],
                        retro_report_key="retro/1", **PROPOSAL)
    box.resolve(id, Resolution(kind="tombstone", link=f"tombstone-{id}"))
    for n in range(3):
        box.record_rereport(id, occurrence_id=f"report/{n}")
    assert _run(root, monkeypatch, FakeLLM([reply("author"), author_reply("human-look"),
                                          requisition_reply("approve")])) == 0
    text = (root / "tickets/human-look/ticket.md").read_text()
    ticket = validate_ticket("human-look", text, root)
    assert ticket.frontmatter.source == "box:retro_finding" and ticket.frontmatter.state == "draft"
    assert box.get(id).resolution == Resolution(kind="ticket", link="human-look")
    bridge, = [e for e in journal.read() if e.body.get("kind") == "retro_ticket_authored"]
    assert bridge.key == "retro-ticket/human-look" and bridge.body == {
        "kind": "retro_ticket_authored", "box_id": id, "retro_report_key": "retro/1", "ticket_stem": "human-look"}


@pytest.mark.parametrize("point", ["bridge", "resolution"])
@pytest.mark.parametrize("after", [False, True])
def test_retro_author_bridge_and_resolution_recover_without_another_call(tmp_path, monkeypatch, point, after):
    from tests.test_retro_box import PROPOSAL
    class Crash(BaseException):
        pass
    root = make_root(tmp_path)
    _routes(root)
    box = _box(root)
    id, _ = box.enqueue(message_class="retro_finding", origin="retro", summary=PROPOSAL["fixed_failure"],
                        retro_report_key="retro/1", **PROPOSAL)
    llm = FakeLLM([reply("author"), author_reply("durable-repair"), requisition_reply("approve")])
    append, resolve = Journal.append, Box.resolve
    def crashed_append(self, type_, body, **kwargs):
        if point == "bridge" and body.get("kind") == "retro_ticket_authored":
            if after:
                append(self, type_, body, **kwargs)
            raise Crash()
        return append(self, type_, body, **kwargs)
    def crashed_resolve(self, message_id, resolution):
        if point == "resolution" and resolution.kind == "ticket":
            if after:
                resolve(self, message_id, resolution)
            raise Crash()
        return resolve(self, message_id, resolution)
    with monkeypatch.context() as patch:
        patch.setattr(Journal, "append", crashed_append)
        patch.setattr(Box, "resolve", crashed_resolve)
        with pytest.raises(Crash):
            _run(root, patch, llm)
    head = git_out(root, "rev-parse", "HEAD").strip()
    assert _run(root, monkeypatch, FakeLLM([])) == 0
    assert git_out(root, "rev-parse", "HEAD").strip() == head
    assert box.get(id).resolution == Resolution(kind="ticket", link="durable-repair")
    bridges = [e for e in _events(root) if e.body.get("kind") == "retro_ticket_authored"]
    assert len(bridges) == 1 and bridges[0].key == "retro-ticket/durable-repair"
    assert len(llm.requests) == 3
