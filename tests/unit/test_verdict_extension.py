import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from chupa import __main__ as entry
from chupa import control, runner
from chupa.journal import EventType
from chupa.serve import Serve


class Journal:
    def __init__(self, events):
        self.events = events

    def read(self):
        return list(self.events)

    def append(self, type, body, *, ticket=None, key=None):
        self.events.append(SimpleNamespace(type=type, body=body, ticket=ticket, key=key))


def event(type, body, ticket="sample", key=None):
    return SimpleNamespace(type=type, body=body, ticket=ticket, key=key)


def test_request_actor_and_parser():
    body = dict(request_id="request-1", lifecycle_id="life", verb="confirm", stem="sample", hold_id=None, actor="extension")
    assert control.validate_request(body, "request-1.json").actor == "extension"
    with pytest.raises(ValueError):
        control.validate_request({**body, "actor": "unknown"}, "request-1.json")
    args = entry._parser().parse_args(["confirm", "sample", "--extension"])
    assert args.extension and args.stem == "sample" and not args.yes


def test_settle_passes_actor():
    body = dict(
        kind=control.CONTROL_DECISION, decision="accepted", reason="matching admission", lifecycle_id="life", verb="confirm", hold_id=None, stem="sample", request_id="request-1", actor="extension"
    )
    journal = Journal([event(EventType.SIGNAL, body, ticket=None)])
    inbox = object.__new__(control.ControlInbox)
    inbox.journal = journal
    callback = AsyncMock(return_value={"refusal": None})
    asyncio.run(inbox.settle_admissions(callback))
    callback.assert_awaited_once_with("sample", "confirm", "ticket-plane/sample/confirm/request-1", "extension")


@pytest.mark.parametrize("extension", [False, True])
def test_repeat_keep_without_ticket(monkeypatch, extension):
    history = [
        event(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}),
        event(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "operator", "ticket_sha": None}),
        event(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}),
    ]
    journal = Journal(history)

    class MissingPath:
        def __truediv__(self, other):
            return self

        def is_file(self):
            return False

    checkout = SimpleNamespace(repo=MissingPath(), git=None, journal=journal, fs=None)
    monkeypatch.setattr(runner, "intake", AsyncMock(return_value=SimpleNamespace(refused={})))
    if extension:
        assert asyncio.run(runner.verdict_locked("sample", checkout, kill=False, extension=True)) == 0
        assert journal.events[-1].body == {"signal": "reject_verdict", "verdict": "keep", "actor": "operator", "ticket_sha": None}
    else:
        with pytest.raises(runner.Refusal, match="already kept at this ticket content"):
            asyncio.run(runner.verdict_locked("sample", checkout, kill=False, extension=False))
        assert len(journal.events) == 3


@pytest.mark.parametrize("actor", ["extension", "operator", "machine"])
def test_serve_forwards_actor(monkeypatch, actor):
    journal = Journal([])
    git = SimpleNamespace(rev_parse=AsyncMock(return_value="base"), _run=AsyncMock(return_value=""))

    class MissingPath:
        def __truediv__(self, other):
            return self

        def is_file(self):
            return False

    checkout = SimpleNamespace(journal=journal, git=git, repo=MissingPath())
    owner = object.__new__(Serve)
    owner.checkout = checkout
    owner.published = {}
    verdict = AsyncMock()
    monkeypatch.setattr(runner, "verdict_locked", verdict)
    assert asyncio.run(owner.apply_verdict("sample", "confirm", "key", actor)) == {"refusal": None}
    verdict.assert_awaited_once_with("sample", checkout, kill=False, extension=actor == "extension")


@pytest.mark.parametrize("refused", [True, False])
def test_live_verdict_intakes_before_publication(monkeypatch, refused):
    from pathlib import Path

    from chupa import tickets
    from chupa.lockfile import LockHeld

    class MissingPath:
        def __truediv__(self, other):
            return self

        def is_file(self):
            return False

    async def held(*args, **kwargs):
        raise LockHeld(Path("chupa.lock"), {"verb": "drain"})

    findings = {"sample": [SimpleNamespace(message="invalid edit")]} if refused else {}
    intake = AsyncMock(return_value=SimpleNamespace(refused=findings))
    published = []
    checkout = SimpleNamespace(
        repo=MissingPath(), git=SimpleNamespace(status_porcelain=AsyncMock(return_value=" M tickets/sample/ticket.md")), journal=Journal([]), fs=None, config=SimpleNamespace(state_dir=Path("state"))
    )
    monkeypatch.setattr(runner, "verdict", held)
    monkeypatch.setattr(tickets, "intake", intake)
    monkeypatch.setattr(control, "read_active", lambda *args: ("life", None))
    monkeypatch.setattr(control, "publish_request", lambda *args: published.append(args[1]))
    if refused:
        with pytest.raises(runner.Refusal, match="invalid edit"):
            asyncio.run(entry._verdict(checkout, "sample", "confirm", None, True, False))
        assert published == []
    else:
        assert asyncio.run(entry._verdict(checkout, "sample", "confirm", None, True, False)) == 0
        assert len(published) == 1 and published[0].stem == "sample"
    intake.assert_awaited_once()
