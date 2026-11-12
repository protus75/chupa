import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

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


def test_shared_admission_refusal_and_replay(monkeypatch):
    class MissingPath:
        def __truediv__(self, other):
            return self

        def is_file(self):
            return False

    journal = Journal([])
    checkout = SimpleNamespace(repo=MissingPath(), journal=journal, git=SimpleNamespace(rev_parse=AsyncMock(return_value="base"), _run=AsyncMock(return_value="")))
    verdict = AsyncMock(side_effect=runner.Refusal("settled", "leave it"))
    monkeypatch.setattr(runner, "verdict_locked", verdict)
    result = asyncio.run(runner.apply_admission("sample", "confirm", "key", "extension", checkout))
    assert result == {"refusal": "settled -- leave it"}
    verdict.assert_awaited_once_with("sample", checkout, kill=False, extension=True)
    journal.events.extend([event(EventType.EFFECT_INTENT, {}, key="again"), event(EventType.SIGNAL, {"signal": "draft_confirmed"})])
    verdict.reset_mock()
    assert asyncio.run(runner.apply_admission("sample", "confirm", "again", "operator", checkout)) == {"refusal": None}
    verdict.assert_not_awaited()


def test_build_control_known_rule(monkeypatch):
    class FakePath:
        def __init__(self, parts=()):
            self.parts = parts

        def __truediv__(self, part):
            return FakePath(self.parts + (str(part),))

        def is_file(self):
            return self.parts == ("tickets/existing/ticket.md",)

    journal = Journal([event(EventType.SIGNAL, {}, ticket="journaled")])
    checkout = SimpleNamespace(config=SimpleNamespace(state_dir=FakePath()), repo=FakePath(), fs=object(), journal=journal, clock=lambda: None, sleep=AsyncMock())
    monkeypatch.setattr(entry, "ProviderSession", lambda *args, **kwargs: object())
    consumer = entry.build_control(checkout)
    assert consumer.inbox.known("existing")
    assert consumer.inbox.known("journaled")
    assert not consumer.inbox.known("absent")


def test_drain_logs_refusal(monkeypatch):
    from pathlib import PurePath

    from chupa import drain

    log = SimpleNamespace(event=Mock())
    monkeypatch.setattr(drain, "EngineLog", lambda *args: log)
    monkeypatch.setattr(drain.Redactor, "from_config", lambda *args: None)
    monkeypatch.setattr(runner, "apply_admission", AsyncMock(return_value={"refusal": "settled"}))

    async def settle(callback):
        assert await callback("done", "confirm", "key", "extension") == {"refusal": "settled"}

    checkout = SimpleNamespace(config=SimpleNamespace(state_dir=PurePath("state")), env={}, clock=None, control=SimpleNamespace(inbox=SimpleNamespace(settle_admissions=settle)))
    asyncio.run(drain.settle_admissions(checkout))
    log.event.assert_called_once_with("verdict_refused", stem="done", verb="confirm", reason="settled")


def test_serve_delegates_admission(monkeypatch):
    owner = object.__new__(Serve)
    owner.checkout = object()
    owner.published = {}
    shared = AsyncMock(return_value={"refusal": "no"})
    monkeypatch.setattr(runner, "apply_admission", shared)
    owner.log = SimpleNamespace(event=Mock())
    assert asyncio.run(owner.apply_verdict("dd", "reject", "key", "operator")) == {"refusal": "no"}
    shared.assert_awaited_once_with("dd", "reject", "key", "operator", owner.checkout)
    owner.log.event.assert_called_once_with("verdict_refused", stem="dd", verb="reject", reason="no")
