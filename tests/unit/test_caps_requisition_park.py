"""Requisition parks do not consume the failed-attempt budget."""

from chupa.caps import failed_attempt, failed_attempts, spent
from chupa.config import Caps
from chupa.journal import Event, EventType


def events_for(bodies):
    return [Event(1, EventType.STATE_TRANSITION, "2026-01-01T00:00:00+00:00", "red", None, body) for body in bodies]


def test_only_requisition_premise_is_exempt():
    assert not failed_attempt({"to": "premise_failed", "stage": "requisition"})
    assert failed_attempt({"to": "premise_failed", "stage": "implement"})
    assert failed_attempt({"to": "premise_failed"})


def test_requisition_parks_do_not_spend_attempts():
    snag = {"to": "premise_failed", "stage": "requisition"}
    events = events_for([snag] * 5)
    assert failed_attempts(events, "red") == 0
    assert spent(Caps(), events, "red") is None


def test_other_failures_still_spend_attempts():
    events = events_for([{"to": "premise_failed", "stage": "requisition"}] * 4 + [{"to": "gate_failed"}] * 5)
    assert failed_attempts(events, "red") == 5
    assert spent(Caps(), events, "red") == "attempts"
