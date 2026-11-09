from datetime import UTC, datetime

from chupa.journal import Event, EventType
from chupa.stats import project_stats, window_start


def test_latest_settled_excludes_future_and_replaces_earlier_event():
    events = [
        Event(1, EventType.STATE_TRANSITION, "2026-01-01T10:00:00+00:00", "a", None, {"to": "merged"}),
        Event(1, EventType.STATE_TRANSITION, "2026-01-01T11:00:00+00:00", "a", None, {"to": "rejected"}),
        Event(1, EventType.STATE_TRANSITION, "2026-01-01T13:00:00+00:00", "b", None, {"to": "merged"}),
    ]
    now = datetime(2026, 1, 1, 12, tzinfo=UTC)

    assert window_start(events, now, "1t") == datetime(2026, 1, 1, 11, tzinfo=UTC)
    assert project_stats(events, {}, {}, now=now, window="7d")["throughput"]["settled"] == {
        "merged": 0,
        "already_satisfied": 0,
        "rejected": 1,
    }
