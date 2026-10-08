"""The shared hardening round-state fold (CHUPA_PLAN.md section 11.4)."""

from collections.abc import Iterable
from typing import Literal

from chupa.journal import TERMINAL_STATES, Event, EventType

RoundState = Literal["open", "closed"]

ROUND_STATES: dict[str, RoundState] = {
    "running": "open",
    "merged": "closed",
    "already_satisfied": "closed",
    "rejected": "closed",
    "premise_failed": "closed",
    "gate_failed": "open",
    "invalid_artifact": "open",
    "timeout": "open",
    "infra_error": "open",
    "abandoned": "open",
    "budget_exceeded": "open",
}


def round_state(events: Iterable[Event], hardener: str) -> RoundState:
    """The first closing terminal closes the round forever, regardless of later runs."""
    for event in events:
        if event.type == EventType.STATE_TRANSITION and event.ticket == hardener:
            state = event.body.get("to")
            if state in TERMINAL_STATES and (
                    ROUND_STATES[state] == "closed" or event.body.get("routed") == "reject_queue"):
                return "closed"
    return "open"
