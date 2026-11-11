"""Reproduce an operator keep failing to release a premise park."""

import json

from chupa.drain import parked_blob
from chupa.journal import Event, EventType


def event(kind, body):
    return Event(1, kind, "2026-01-01T00:00:00+00:00", "work", None, body)


events = [
    event(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": "B"}),
    event(EventType.STATE_TRANSITION, {"to": "premise_failed", "stage": "implement"}),
    event(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "operator"}),
]
passed = parked_blob(events, "work") is None
print(json.dumps({"regression_result": "pass" if passed else "defect"}))
raise SystemExit(0 if passed else 1)
