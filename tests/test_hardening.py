"""Hardening round closure and its lineage cap (CHUPA_PLAN.md sections 11.1, 11.4)."""

from datetime import UTC, datetime

import pytest

from chupa.audit import audit, audit_journal
from chupa.caps import CAPS, DECLARED_CAPS, consume, draws, remaining, spent
from chupa.config import Caps
from chupa.hardening import ROUND_STATES, round_state
from chupa.journal import TERMINAL_STATES, EventType, Journal


def journal(tmp_path):
    return Journal(tmp_path, lambda: datetime(2026, 10, 8, tzinfo=UTC))


def test_round_state_maps_every_run_state():
    assert set(ROUND_STATES) == TERMINAL_STATES | {"running"}
    assert set(ROUND_STATES.values()) <= {"open", "closed"}


@pytest.mark.parametrize("terminal,expected", [
    ("merged", "closed"), ("already_satisfied", "closed"),
    ("rejected", "closed"), ("premise_failed", "closed"),
    ("gate_failed", "open"), ("invalid_artifact", "open"),
    ("timeout", "open"), ("infra_error", "open"),
    ("abandoned", "open"), ("budget_exceeded", "open"),
])
def test_round_state_closes_per_section_11_4(tmp_path, terminal, expected):
    j = journal(tmp_path)
    assert round_state(j.read(), "hardener") == "open"
    j.append(EventType.STATE_TRANSITION, {"to": "merged"}, ticket="other")
    j.append(EventType.SIGNAL, {"to": "merged", "routed": "reject_queue"}, ticket="hardener")
    j.append(EventType.STATE_TRANSITION, {"to": "running", "routed": "reject_queue"}, ticket="hardener")
    assert round_state(j.read(), "hardener") == "open"
    j.append(EventType.STATE_TRANSITION, {"to": terminal}, ticket="hardener")
    assert round_state(iter(j.read()), "hardener") == expected
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="hardener")
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket="hardener")
    assert round_state(j.read(), "hardener") == expected
    j.append(EventType.STATE_TRANSITION, {"to": "gate_failed", "routed": "reject_queue"}, ticket="hardener")
    assert round_state(j.read(), "hardener") == "closed"
    j.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="hardener")
    assert round_state(j.read(), "hardener") == "closed"


@pytest.mark.parametrize("terminal", sorted(TERMINAL_STATES))
def test_every_reject_routed_terminal_closes(tmp_path, terminal):
    j = journal(tmp_path)
    j.append(EventType.STATE_TRANSITION, {"to": terminal, "routed": "reject_queue"}, ticket="hardener")
    assert round_state(j.read(), "hardener") == "closed"


def test_hardening_draws_pass_the_declared_cap_audit(tmp_path):
    j = journal(tmp_path)
    consume(j, "held", "hardening", "ticket-blob")
    assert DECLARED_CAPS == CAPS + ("hardening",)
    assert audit(j.read_segments()) == []
    assert audit_journal(j) == []
    assert [v.invariant for v in audit(j.read_segments(), caps=CAPS)] == ["declared_cap"]


def test_hardening_uses_the_lineage_fold_without_blocking_dispatch(tmp_path):
    j = journal(tmp_path)
    config = Caps(hardening=2)
    consume(j, "held", "hardening", "old-blob")
    consume(j, "held", "hardening", "new-blob")
    consume(j, "other", "hardening", "other-blob")
    assert draws(j.read(), "held", "hardening") == 2
    assert remaining(config, j.read(), "held", "hardening") == 0
    assert spent(config, iter(j.read()), "held") is None
    j.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, ticket="held")
    assert remaining(config, j.read(), "held", "hardening") == 0
    j.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "operator"}, ticket="held")
    assert remaining(config, j.read(), "held", "hardening") == 2
