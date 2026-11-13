"""Unit coverage for the shared author helpers."""

import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa.author import committed, goal
from chupa.git import GitError


def test_committed_true_when_rev_parse_resolves():
    async def rev_parse(repo, ref):
        assert repo == Path("repo") and ref == "HEAD:tickets/live/ticket.md"
        return "abc123"

    checkout = SimpleNamespace(repo=Path("repo"), git=SimpleNamespace(rev_parse=rev_parse))
    assert asyncio.run(committed(checkout, Path("tickets/live/ticket.md"))) is True


def test_committed_false_on_git_error():
    async def rev_parse(repo, ref):
        raise GitError(["git", "rev-parse", ref], 1, "", "missing")

    checkout = SimpleNamespace(repo=Path("repo"), git=SimpleNamespace(rev_parse=rev_parse))
    assert asyncio.run(committed(checkout, Path("tickets/missing/ticket.md"))) is False


def test_goal_first_nonblank_line():
    assert goal("x\n## Goal / Why\n\n  first  \nsecond\n") == "first"
    assert goal("x\nno heading\n") == ""


def test_retro_ticket_reopen_boundary():

    from chupa.author import record_retro_ticket
    from chupa.box import BoxError
    from chupa.journal import EventType
    from tests.unit.test_retro_recurrence import MemoryJournal, message

    journal = MemoryJournal()
    original = message()
    record_retro_ticket(journal, original, "old-fix")
    with pytest.raises(BoxError):
        record_retro_ticket(journal, original, "new-fix")
    journal.append(EventType.EFFECT_INTENT, {"recurrences": 1, "reopened": True}, key="retro-recurrence/box-1/occurrence")
    record_retro_ticket(journal, original.model_copy(update={"reopen": True}), "new-fix")
    assert [e.key for e in journal.read() if e.body.get("kind") == "retro_ticket_authored"] == ["retro-ticket/old-fix", "retro-ticket/new-fix"]


@pytest.mark.asyncio
async def test_recovery_ignores_completions_before_reopen(monkeypatch):
    import json

    from chupa import author
    from chupa.journal import EventType
    from tests.unit.test_retro_recurrence import MemoryJournal, message

    journal = MemoryJournal()

    def completion(stem, seq):
        journal.append(EventType.EFFECT_COMPLETION, {"result": {"text": json.dumps({"stem": stem, "ticket": "ticket"})}}, key=f"llm/author/{seq}/author/1/1")
        journal.append(EventType.EFFECT_COMPLETION, {"result": stem + "-sha"}, key=f"ticket-plane/{stem}/author")

    completion("old-fix", 1)
    journal.append(EventType.EFFECT_INTENT, {"recurrences": 1, "reopened": True}, key="retro-recurrence/box-1/occurrence")

    async def show(*args):
        return "ticket"

    checkout = SimpleNamespace(journal=journal, repo=Path("/repo"), git=SimpleNamespace(_run=show))
    resolved = []
    box = SimpleNamespace(resolve=lambda id, resolution: resolved.append(resolution))
    reopened = message(reopen=True)
    assert await author.recover_retro_ticket(checkout, box, reopened) is None
    completion("new-fix", 2)
    monkeypatch.setattr(author, "validate_ticket", lambda *args: SimpleNamespace(frontmatter=SimpleNamespace(source="box:retro_finding")))
    result = await author.recover_retro_ticket(checkout, box, reopened)
    assert result.stem == "new-fix" and resolved[0].link == "new-fix"


def test_gate_admits_own_passed_stem_only(monkeypatch):
    from chupa import author

    events = []
    checkout = SimpleNamespace(repo=Path("/repo"), journal=SimpleNamespace(read=lambda: events))
    monkeypatch.setattr(author, "validate_ticket", lambda stem, text, repo: None)
    candidate = author.AuthorReply(stem="draft-stem", ticket="t")
    gate = author.AuthorGate(checkout)
    assert gate.check(candidate, checkout.repo).verdict == "pass"
    events.append(SimpleNamespace(ticket="draft-stem", key="llm/author/1/requisition_review/7/1"))
    assert gate.check(candidate, checkout.repo).verdict == "pass"
    report = author.AuthorGate(checkout).check(candidate, checkout.repo)
    assert report.verdict == "fail"
    assert any("already named in the journal" in finding.message for finding in report.findings)


@pytest.mark.asyncio
async def test_author_renders_inputs_and_passes_prior_review(monkeypatch):
    from chupa import author as module
    from chupa.artifacts import Finding
    from chupa.requisition import FIRST_REVIEW
    from tests.unit.test_retro_recurrence import MemoryJournal, message

    class Done(Exception):
        pass

    async def ls_files(repo):
        return ["tracked.py"]

    async def open_tickets(checkout):
        return "none"

    priors, inputs_seen = [], []
    finding = Finding(code="gap", message="unique unit finding", paved_road="repair")

    async def review(*args, **kwargs):
        priors.append(kwargs["prior"])
        return SimpleNamespace(verdict="snag" if len(priors) == 1 else "approve", findings=[finding] if len(priors) == 1 else [], calls=1)

    async def run(stage, *args, **kwargs):
        stage.render(None, [])
        await stage.review(module.AuthorReply(stem="one", ticket="first"), 1)
        await stage.review(module.AuthorReply(stem="one", ticket="second"), 2)
        raise Done

    monkeypatch.setattr(Path, "read_text", lambda self: "guide text" if self.name == "host-authoring.md" else "spec")
    monkeypatch.setattr(module, "load_spec", lambda text: SimpleNamespace(meta=SimpleNamespace(effort="medium")))
    monkeypatch.setattr(module, "render", lambda spec, inputs: inputs_seen.append(inputs) or "rendered")
    monkeypatch.setattr(module, "list_open_tickets", open_tickets)
    monkeypatch.setattr(module, "review_ticket", review)
    monkeypatch.setattr(module.AuthorGate, "check", lambda *args: SimpleNamespace(verdict="pass"))
    monkeypatch.setattr(module, "stamp", lambda text, *args: text)
    monkeypatch.setattr(module, "validate_ticket", lambda *args: SimpleNamespace(scope_fence=(), frontmatter=SimpleNamespace(gate_bypass=False)))
    monkeypatch.setattr(module, "resolve_baseline", lambda *args, **kwargs: SimpleNamespace(binds=False))
    monkeypatch.setattr(module, "start_state", lambda *args, **kwargs: "draft")
    journal = MemoryJournal()
    checkout = SimpleNamespace(
        repo=Path("/repo"),
        git=SimpleNamespace(ls_files=ls_files),
        journal=journal,
        config=SimpleNamespace(state_dir=Path("/state"), review=SimpleNamespace(coverage_map=None), routing_default_tier="medium"),
    )
    box = SimpleNamespace(root=Path("/box"))
    with pytest.raises(Done):
        await module.author(checkout, SimpleNamespace(run=run), box, message().model_copy(update={"verdict": SimpleNamespace(rationale="observed")}), 1)
    assert priors[0] == FIRST_REVIEW
    assert "unique unit finding" in priors[1] and "+second" in priors[1]
    assert inputs_seen[0]["guide"] == "guide text"
    assert "kind: bug" in inputs_seen[0]["skeletons"] and "kind: feature" in inputs_seen[0]["skeletons"]
