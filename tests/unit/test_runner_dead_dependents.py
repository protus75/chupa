import asyncio
from types import SimpleNamespace

from chupa import runner
from chupa.journal import EventType


class Journal:
    def __init__(self, events):
        self.events = events

    def read(self):
        return list(self.events)

    def append(self, type, body, *, ticket=None, key=None):
        self.events.append(SimpleNamespace(type=type, body=body, ticket=ticket, key=key))


def test_dead_dependents_skips_invalid_confirmed_ticket(tmp_path, monkeypatch):
    ticket = """---
state: confirmed
source: human
priority: P2
kind: feature
---
## Depends on
{depends}
## Context
- context.py
## Goal / Why
A goal.
## Scope in / Scope out
A scope.
## Scope fence
- context.py
## Acceptance criteria
1. `check` succeeds.
## Verification
```
check
```
## Definition of rejected
Failure.
## Time budget
- expected: 10m
- stuck: 20m
"""
    (tmp_path / "context.py").write_text("context\n")
    for stem, content in (
        ("aaa-wip", "---\nstate: confirmed\n---\nUnfinished.\n"),
        ("parent", ticket.format(depends="none")),
        ("child", ticket.format(depends="- parent")),
    ):
        path = tmp_path / "tickets" / stem / "ticket.md"
        path.parent.mkdir(parents=True)
        path.write_text(content)
    journal = Journal([SimpleNamespace(type=EventType.STATE_TRANSITION, body={"to": "rejected"}, ticket="parent", key=None)])
    calls = []
    box = SimpleNamespace(enqueue=lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr("chupa.daemon.storm_producer", lambda **kwargs: box)
    checkout = SimpleNamespace(repo=tmp_path, config=SimpleNamespace(state_dir=tmp_path / "state"), fs=None, clock=None, journal=journal)

    asyncio.run(runner._dead_dependents("parent", checkout))

    signals = [e.body for e in journal.events if e.type == EventType.SIGNAL and e.ticket == "child"]
    assert signals == [{"signal": "dead_dependency", "dead": "parent"}]
    assert len(calls) == 1 and calls[0]["origin"] == "child"
