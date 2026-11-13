import asyncio
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

import pytest

from chupa import __main__ as entry
from chupa import runner, status, triage
from chupa.box import UnknownBoxId
from chupa.journal import EventType
from chupa.tickets import TicketInvalid, validate_ticket


def event(state):
    return NS(type=EventType.STATE_TRANSITION, ticket="item", body={"to": state}, key=None)


def test_stem_admissions():
    assert status.order_admission("item", [], False, None).message == "tickets/item/ticket.md does not exist"
    assert status.order_admission("item", [event("merged")], True, None).outcome == "refuse"
    running = [event("running")]
    assert status.order_admission("item", running, True, None).outcome == "admit"
    assert status.order_admission("item", running, True, object()).outcome == "refuse"
    with pytest.raises(TicketInvalid):
        validate_ticket("item", "not a ticket", Path("/repo"))
    assert status.order_admission("item", [], True, None).outcome == "admit"
    assert status.lint_admission("item", [], False).outcome == "refuse"
    assert status.lint_admission("item", [event("rejected")], True).outcome == "noop"
    assert status.lint_admission("item", [], True).outcome == "admit"


def test_box_admissions():
    pending = NS(id="one", resolution=None)
    resolved = NS(id="two", resolution=NS(link="ticket-2"))
    for admit in (status.triage_admission, status.dismiss_admission):
        assert admit("missing", [pending]).message == "unknown box id missing"
        assert admit("one", [pending, resolved]).outcome == "admit"
        assert admit("two", [pending, resolved]).message == "two: already resolved -> ticket-2"


def test_order_refusal(monkeypatch):
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    checkout = NS(repo=Path("/repo"))
    with pytest.raises(runner.Refusal, match="tickets/item/ticket.md does not exist"):
        entry._order(checkout, "item", "P1", None)


def test_box_verbs(monkeypatch):
    resolved = NS(id="two", resolution=NS(link="ticket-2"))

    class Box:
        def __init__(self, *args, **kwargs):
            pass

        def messages(self):
            return [resolved]

        def get(self, id):
            return resolved

    monkeypatch.setattr(triage, "Box", Box)
    monkeypatch.setattr(triage.Driver, "from_config", lambda *args, **kwargs: NS())
    checkout = NS(config=NS(state_dir=Path("/state")), fs=None, journal=NS(read=lambda: []), env={}, clock=None, sleep=None)
    for call in (triage.triage_pass(checkout, None, ["missing"]), triage.dismiss(checkout, ["missing"])):
        with pytest.raises(UnknownBoxId, match="unknown box id missing"):
            asyncio.run(call)
    assert asyncio.run(triage.dismiss(checkout, ["two"])) == ["two: already resolved -> ticket-2"]


def test_lint_refusal_and_skip(monkeypatch, capsys):
    monkeypatch.setattr(Path, "iterdir", lambda self: iter([]))
    monkeypatch.setattr(Path, "resolve", lambda self: self)
    monkeypatch.setattr(Path, "is_file", lambda self: self.parent.name == "settled")
    git = NS(git_common_dir=AsyncMock(return_value=Path("/repo/.git")), status_porcelain=AsyncMock(return_value=""))
    checkout = NS(repo=Path("/repo"), config=NS(state_dir=Path("/state")), journal=NS(read=lambda: [NS(type=EventType.STATE_TRANSITION, ticket="settled", body={"to": "merged"})]), git=git)
    assert asyncio.run(entry._lint(checkout, ["missing", "settled"])) == 2
    output = capsys.readouterr().out
    assert "tickets/missing/ticket.md: no ticket file" in output
    assert "lint: 0/1 tickets valid" in output
