"""On-demand review uses the committed ticket and records its verdict."""

import json

from chupa.__main__ import main
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from tests.integration.test_cli import ENV, git_out, ticket, write
from tests.integration.test_drain import Clock, commit_ticket, confirmed, make_root


def run(root, monkeypatch, llm, stem):
    monkeypatch.setattr("chupa.__main__.ProviderLLM", lambda *args, **kwargs: llm)
    return main(["review", stem], cwd=root, env=ENV, clock=Clock())


def verdicts(root):
    return [e for e in Journal(root / ".chupa/state", Clock()).read() if e.type == EventType.SIGNAL and e.body.get("signal") == "requisition_verdict"]


def reply(verdict, findings=None):
    return json.dumps({"verdict": verdict, "summary": "reviewed", "findings": findings or []})


def test_review_approve_journals_verdict_for_committed_blob(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    write(root, "candidate", ticket())
    assert run(root, monkeypatch, FakeLLM([reply("approve")]), "candidate") == 0
    [event] = verdicts(root)
    assert event.body["verdict"] == "approve"
    assert event.body["ticket_sha"] == git_out(root, "rev-parse", "main:tickets/candidate/ticket.md").strip()
    assert "state: confirmed" in git_out(root, "show", "main:tickets/candidate/ticket.md")


def test_review_snag_prints_findings_and_exits_1(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    write(root, "candidate", ticket())
    finding = {"code": "fence", "path": "thing.py", "line": 7, "message": "missing caller", "paved_road": "add caller"}
    assert run(root, monkeypatch, FakeLLM([reply("snag", [finding])]), "candidate") == 1
    assert "- [fence] thing.py:7 missing caller (add caller)" in capsys.readouterr().out
    assert verdicts(root)[0].body["verdict"] == "snag"


def test_review_refuses_without_a_model_call(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    commit_ticket(root, "merged", confirmed())
    Journal(root / ".chupa/state", Clock()).append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="merged")
    llm = FakeLLM([])
    for stem in ("missing", "merged"):
        assert run(root, monkeypatch, llm, stem) == 2
    assert llm.requests == []


def test_review_unmerged_dependency_is_provisional(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    commit_ticket(root, "dependency", confirmed())
    commit_ticket(root, "candidate", confirmed("- dependency"))
    llm = FakeLLM([reply("approve")])
    assert run(root, monkeypatch, llm, "candidate") == 0
    output = capsys.readouterr().out
    assert "review candidate: provisional, not recorded -- depends on unmerged dependency; the drain reviews it again before its first run" in output
    assert "review candidate: approve" in output
    assert len(llm.requests) == 1
    assert verdicts(root) == []
