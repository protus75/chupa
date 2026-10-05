"""The `status` projection (CHUPA_PLAN.md section 13 touchpoint 5): a deterministic, write-free fold of the journal.

A projection, never an authority: no gate or dispatch decision reads its rendering.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from chupa.journal import EventType, Event
from chupa.tickets import INTAKE_SIGNAL


@dataclass(frozen=True)
class Status:
    merged: tuple[str, ...]
    in_flight: tuple[str, ...]
    blocked: tuple[tuple[str, str], ...]  # (stem, the non-merged terminal its last run ended in)
    intake: tuple[tuple[str, str, str, str], ...]  # (stem, source, state, commit) per intake commit
    spend_usd: float


def last_states(events: Iterable[Event]) -> dict[str, str]:
    """Each stem's latest run-state transition target."""
    return {e.ticket: e.body["to"] for e in events
            if e.type == EventType.STATE_TRANSITION and e.ticket is not None and "to" in e.body}


def project(events: Iterable[Event]) -> Status:
    events = list(events)
    last = last_states(events)
    intake = tuple(
        (e.ticket, e.body["source"], e.body["state"], e.body["commit"]) for e in events
        if e.type == EventType.SIGNAL and e.body.get("signal") == INTAKE_SIGNAL and e.ticket is not None
    )
    spend = sum(e.body["cost"].get("usd", 0.0) for e in events
                if e.type == EventType.EFFECT_COMPLETION and isinstance(e.body.get("cost"), dict))
    return Status(
        merged=tuple(sorted(s for s, to in last.items() if to == "merged")),
        in_flight=tuple(sorted(s for s, to in last.items() if to == "running")),
        blocked=tuple(sorted((s, to) for s, to in last.items() if to not in ("merged", "running"))),
        intake=intake,
        spend_usd=spend,
    )


def render(status: Status) -> str:
    def block(name: str, lines: Iterable[str]) -> str:
        return f"{name}:\n" + ("\n".join(f"- {line}" for line in lines) or "(none)")

    return "\n\n".join((
        block("merged", status.merged),
        block("in flight", status.in_flight),
        block("blocked", (f"{stem}: {to}" for stem, to in status.blocked)),
        block("intake", (f"{stem}: source: {source}, state: {state}, commit {commit[:12]}"
                         for stem, source, state, commit in status.intake)),
        f"spend:\n${status.spend_usd:.2f}",
    )) + "\n"
