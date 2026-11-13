import asyncio

import pytest

from chupa.__main__ import main
from chupa.journal import EventType, Journal
from chupa.llm import FakeLLM
from chupa.seams import LocalFileSystem
from chupa.tickets import intake
from tests.integration.test_cli import ENV, Clock, Stages, git_out, ticket, write
from tests.integration.test_drain import make_root
from tests.integration.test_review_command import reply
from tests.integration.test_tickets import VALID, repo


def test_scoped_intake_leaves_invalid_staged_ticket(repo):
    root, git, journal = repo
    write(root, "alpha", VALID)
    write(root, "beta", VALID.replace("priority: P2", "priority: invalid"))
    asyncio.run(git.add(root, ["tickets/beta/ticket.md"]))
    result = asyncio.run(intake(root, git, journal, LocalFileSystem(), stems={"alpha"}))
    assert result.committed == ("alpha",)
    assert "beta" not in result.refused
    assert asyncio.run(git._run(root, "diff", "--cached", "--name-only")).splitlines() == ["tickets/beta/ticket.md"]
    assert asyncio.run(git._run(root, "show", "--name-only", "--format=", "HEAD")).splitlines() == ["tickets/alpha/ticket.md"]


@pytest.mark.parametrize("verb", ["review", "run", "confirm", "reject"])
def test_named_verbs_leave_other_pending_ticket(tmp_path, monkeypatch, verb):
    root = make_root(tmp_path)
    draft = ticket().replace("---\n", "---\nstate: draft\n", 1)
    write(root, "alpha", draft)
    write(root, "beta", draft)
    beta = (root / "tickets/beta/ticket.md").read_bytes()
    monkeypatch.setattr("chupa.__main__.ProviderLLM", lambda *args, **kwargs: FakeLLM([reply("approve")]))
    args = [verb, "alpha"] + (["--yes"] if verb in {"confirm", "reject"} else [])
    assert main(args, cwd=root, env=ENV, clock=Clock(), pipeline=Stages()) == (2 if verb == "confirm" else 0)
    subjects = git_out(root, "log", "--format=%s").splitlines()
    assert "chupa(alpha): ticket" in subjects
    assert "chupa(beta): ticket" not in subjects
    assert (root / "tickets/beta/ticket.md").read_bytes() == beta
    assert git_out(root, "status", "--porcelain", "--", "tickets/beta/").strip()
    events = Journal(root / ".chupa/state", Clock()).read()
    assert not any(e.type == EventType.SIGNAL and e.body.get("signal") == "ticket_intake" and e.ticket == "beta" for e in events)
