"""Reproduce an overruled premise being incorrectly parked."""

import json
import sys

from chupa.drain import parked_blob
from chupa.journal import Event, EventType

history = [
    Event(1, EventType.STATE_TRANSITION, "time", "work", None, {"to": "running", "ticket_sha": "ran-sha"}),
    Event(1, EventType.STATE_TRANSITION, "time", "work", None, {"to": "premise_failed", "stage": "implement", "dispatch": "escalate", "rung": {"tier": "high", "effort": "medium"}}),
]
passed = parked_blob(history, "work") is None
print(json.dumps({"regression_result": "pass" if passed else "defect"}))
sys.exit(0 if passed else 1)
