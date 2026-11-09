from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from chupa.__main__ import _parser
from chupa.drain import _Drain


def test_drain_uses_the_carried_deadline():
    now = datetime(2026, 1, 1, tzinfo=UTC)
    checkout = SimpleNamespace(clock=lambda: now, config=SimpleNamespace(drain=SimpleNamespace(max_runtime_hours=2)))
    carried = now + timedelta(hours=5)
    run = _Drain(checkout, None, frozenset(), deadline=carried)
    assert run.deadline == carried  # Recomputing would give two hours, not five.


def test_drain_computes_its_deadline_when_none_is_carried():
    now = datetime(2026, 1, 1, tzinfo=UTC)
    checkout = SimpleNamespace(clock=lambda: now, config=SimpleNamespace(drain=SimpleNamespace(max_runtime_hours=2)))
    run = _Drain(checkout, None, frozenset(), deadline=None)
    assert run.deadline == now + timedelta(hours=2)  # No deadline or a default duration differs.


def test_drain_parser_reads_a_carried_deadline():
    args = _parser().parse_args(["drain", "--deadline", "2026-01-01T02:00:00+00:00"])
    assert args.deadline == datetime(2026, 1, 1, 2, tzinfo=UTC)  # Dropping or retaining the string differs.
    assert _parser().parse_args(["drain"]).deadline is None  # Omission must not invent a deadline.
