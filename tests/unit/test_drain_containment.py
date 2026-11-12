"""Exercise dispatch containment using an in-memory journal and tasks."""

import asyncio
from types import SimpleNamespace

import pytest

from chupa.drain import _Drain
from chupa.journal import EventType


class Journal:
    def __init__(self):
        self.events = []

    def append(self, kind, body, *, ticket):
        self.events.append(SimpleNamespace(type=kind, body=body, ticket=ticket))

    def read(self):
        return self.events[:]


async def exercise(*, terminal=False, control_failure=False):
    journal = Journal()
    checkout = SimpleNamespace(journal=journal, control=None, sleep=asyncio.sleep)
    error = IsADirectoryError("directory")

    async def dispatch(ticket):
        if terminal:
            journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket=ticket.stem)
        raise error

    run = _Drain.__new__(_Drain)
    run.c, run.dispatch, run.last_dispatched = checkout, dispatch, None
    if control_failure:

        async def controlled(task, abort, sleep):
            await asyncio.gather(task, return_exceptions=True)
            raise RuntimeError("monitor failed")

        run._await_controlled = controlled
    await run._run_one(SimpleNamespace(stem="work"), False, "sha")
    return [event.body for event in journal.events]


@pytest.mark.asyncio
async def test_handler_appends_infra_error_when_no_terminal_follows_running():
    assert await exercise() == [{"to": "running", "ticket_sha": "sha"}, {"to": "infra_error", "stage": "dispatch", "reason": "dispatch_exception", "error": "IsADirectoryError: directory"}]


@pytest.mark.asyncio
async def test_handler_appends_nothing_when_terminal_follows_running():
    assert await exercise(terminal=True) == [{"to": "running", "ticket_sha": "sha"}, {"to": "gate_failed"}]


@pytest.mark.asyncio
async def test_handler_reraises_non_dispatch_exception():
    with pytest.raises(RuntimeError, match="monitor failed"):
        await exercise(control_failure=True)
