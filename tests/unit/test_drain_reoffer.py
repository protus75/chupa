"""Re-offer cap draws for terminal outcomes."""

import pytest

from chupa.drain import record_reoffer
from chupa.journal import Event, EventType


class JournalFake:
    def __init__(self):
        self.entries = []

    def append(self, kind, body, *, ticket):
        self.entries.append((kind, body, ticket))


def reoffer(body):
    journal = JournalFake()
    history = [Event(1, EventType.STATE_TRANSITION, "2026-01-01T00:00:00+00:00", "work", None, body)]
    record_reoffer(journal, history, "work", "new-sha")
    return [entry for entry in journal.entries if entry[0] == EventType.CAP_CONSUMED]


def test_infra_error_reoffer_draws_no_retry():
    assert reoffer({"to": "infra_error"}) == []  # An unconditional retry draw spends two caps.


def test_timeout_reoffer_draws_no_retry():
    assert reoffer({"to": "timeout"}) == []  # Treating timeouts as ordinary failures spends two caps.


@pytest.mark.parametrize("terminal", ["infra_error", "timeout"], ids=["infra", "timeout"])
def test_escalated_reoffer_keeps_rung_draw(terminal):
    rung = {"tier": "high", "effort": "max"}
    assert reoffer({"to": terminal, "rung": rung}) == [
        (EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "new-sha", "rung": rung}, "work")
    ]  # Skipping escalations or dropping the rung loses the next capability.


@pytest.mark.parametrize("terminal", ["gate_failed", "abandoned"])
def test_other_reoffer_draws_retry(terminal):
    assert reoffer({"to": terminal}) == [(EventType.CAP_CONSUMED, {"cap": "retry", "ticket_sha": "new-sha"}, "work")]  # Skipping all failed terminals leaves these re-offers undrawn.


@pytest.mark.parametrize("body", [{"to": "premise_failed"}, {"to": "infra_error", "provider_drought": {"tier": "high"}}], ids=["premise", "drought"])
def test_existing_exclusions_draw_nothing(body):
    assert reoffer(body) == []  # Removing the existing exclusions spends retry on these terminals.
