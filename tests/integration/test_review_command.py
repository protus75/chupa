"""On-demand review uses the committed ticket and records its verdict."""

import json

from chupa.__main__ import main
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.lockfile import Lockfile
from chupa.reconcile import orphans
from chupa.requisition import FIRST_REVIEW
from chupa.status import last_states
from tests.integration.test_cli import ENV, git_out, ticket, write
from tests.integration.test_drain import Clock, commit_ticket, confirmed, make_root


def run(root, monkeypatch, llm, stem):
    monkeypatch.setattr("chupa.__main__.ProviderLLM", lambda *args, **kwargs: llm)
    return main(["review", stem], cwd=root, env=ENV, clock=Clock())


def verdicts(root):
    return [e for e in Journal(root / ".chupa/state", Clock()).read() if e.type == EventType.SIGNAL and e.body.get("signal") == "requisition_verdict"]


def reply(verdict, findings=None):
    return json.dumps({"verdict": verdict, "summary": "reviewed", "findings": findings or []})


def test_review_preflight_failure_refuses(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    write(root, "candidate", ticket())

    async def preflight(self):
        return ["probe refused"]

    monkeypatch.setattr("chupa.providers.ProviderLLM.preflight", preflight)
    assert main(["review", "candidate"], cwd=root, env=ENV, clock=Clock()) == 2
    assert "chupa review: probe refused" in capsys.readouterr().err
    assert verdicts(root) == []
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="probe", clock=Clock())
    lock.acquire()
    lock.release()


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


def test_review_releases_checkout_lock_during_call(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    write(root, "candidate", ticket())
    state_dir = root / ".chupa/state"
    journal = Journal(state_dir, Clock())
    journal.append(EventType.STATE_TRANSITION, {"to": "confirmed"}, ticket="candidate")
    observed = []

    def probe(request):
        lock = Lockfile(state_dir, verb="drain", instance_id="probe", clock=Clock())
        lock.acquire()
        try:
            events = journal.read()
            observed.append((lock.held, orphans(events), last_states(events)["candidate"]))
        finally:
            lock.release()
        return reply("approve")

    assert run(root, monkeypatch, FakeLLM([probe]), "candidate") == 0
    assert observed == [(True, [], "confirmed")]
    assert last_states(journal.read())["candidate"] == "confirmed"
    assert [event.body["verdict"] for event in verdicts(root)] == ["approve"]


def test_review_committed_ticket_while_checkout_locked(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    commit_ticket(root, "candidate", confirmed())
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="engine", clock=Clock())
    lock.acquire()
    try:
        llm = FakeLLM([reply("approve")])
        assert run(root, monkeypatch, llm, "candidate") == 0
        [event] = verdicts(root)
        assert event.body["verdict"] == "approve"
        assert event.body["ticket_sha"] == git_out(root, "rev-parse", "main:tickets/candidate/ticket.md").strip()
        assert len(llm.requests) == 1
    finally:
        lock.release()


def test_review_changed_ticket_refuses_while_checkout_locked(tmp_path, monkeypatch, capsys):
    root = make_root(tmp_path)
    commit_ticket(root, "candidate", confirmed())
    path = root / "tickets/candidate/ticket.md"
    path.write_text(path.read_text() + "\nPending edit\n")
    lock = Lockfile(root / ".chupa/state", verb="drain", instance_id="engine", clock=Clock())
    lock.acquire()
    try:
        llm = FakeLLM([])
        assert run(root, monkeypatch, llm, "candidate") == 2
        assert llm.requests == []
        assert verdicts(root) == []
        assert "wait for the running engine to commit the ticket through intake, or stop it, then retry `review candidate`" in capsys.readouterr().err
    finally:
        lock.release()


def test_review_uses_previous_findings_after_edit(tmp_path, monkeypatch):
    root = make_root(tmp_path)
    commit_ticket(root, "candidate", confirmed())
    finding = {"code": "fence", "message": "missing caller", "paved_road": "add caller"}
    llm = FakeLLM([reply("snag", [finding]), reply("approve")])
    assert run(root, monkeypatch, llm, "candidate") == 1
    path = root / "tickets/candidate/ticket.md"
    path.write_text(path.read_text().replace("## Goal / Why", "## Goal / Why\nChanged."))
    git_out(root, "add", "tickets/candidate/ticket.md")
    git_out(root, "commit", "-m", "edit ticket")
    assert run(root, monkeypatch, llm, "candidate") == 0
    blocks = [r.rendered.split("<<chupa-data:begin prior_review>>\n", 1)[1].split("\n<<chupa-data:end prior_review>>", 1)[0] for r in llm.requests]
    assert blocks[0] == FIRST_REVIEW
    assert "missing caller" in blocks[1] and "+Changed." in blocks[1]
