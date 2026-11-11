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
