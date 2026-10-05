"""Lineage-scoped failure-spine cap accounting (CHUPA_PLAN.md section 11.2)."""

from collections.abc import Iterable

from chupa.config import Caps
from chupa.journal import Event, EventType, Journal

CAPS = ("diagnosis", "retry", "infra", "premise_bounce")


def _check(cap: str) -> None:
    if cap not in CAPS:
        raise ValueError(f"cap {cap!r} is not one of CAPS {CAPS}")


def draws(events: Iterable[Event], stem: str, cap: str) -> int:
    """Count this stem's draws for one cap across all ticket content revisions."""
    _check(cap)
    history = tuple(events)
    keep = next((i for i, e in reversed(list(enumerate(history)))
                 if e.type == EventType.SIGNAL and e.ticket == stem
                 and e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "keep"
                 and e.body.get("actor") == "operator"), -1)
    return sum(e.type == EventType.CAP_CONSUMED and e.ticket == stem and e.body.get("cap") == cap
               for e in history[keep + 1:])


def remaining(caps_config: Caps, events: Iterable[Event], stem: str, cap: str) -> int:
    _check(cap)
    return getattr(caps_config, cap) - draws(events, stem, cap)


def spent(caps_config: Caps, events: Iterable[Event], stem: str) -> str | None:
    # Materialize once: callers may pass a journal iterator, not only a list.
    history = tuple(events)
    return next((cap for cap in CAPS if remaining(caps_config, history, stem, cap) <= 0), None)


def consume(journal: Journal, stem: str, cap: str, ticket_sha: str) -> None:
    _check(cap)
    journal.append(EventType.CAP_CONSUMED, {"cap": cap, "ticket_sha": ticket_sha}, ticket=stem)


def spent_reason(cap: str) -> str:
    return f"{cap} cap spent"
