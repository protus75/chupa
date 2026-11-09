"""Unit coverage for the shared author helpers."""

import asyncio
from pathlib import Path
from types import SimpleNamespace

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
