"""Dormant per-call adapter event consumer (19.P4.watchdog-event-stream)."""

from collections.abc import Callable


class EventConsumer:
    """Receive scrubbed provider objects in order; detection belongs to a later row."""

    def __init__(self, on_event: Callable[[dict], None]) -> None:
        self._on_event = on_event

    def consume(self, event: dict) -> None:
        self._on_event(event)
