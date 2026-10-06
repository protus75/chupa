"""Debounced ticket-change observation for the dormant scheduler (section 9)."""

from collections.abc import Callable
from typing import Protocol

from chupa.journal import EventType
from chupa.scheduler import PendingTicket, Scheduler
from chupa.seams import Sleep


class JournalWriter(Protocol):
    def append(self, type: str, body: dict[str, str], *, ticket: str | None = None, key: str | None = None) -> object:
        ...


Parse = Callable[[str, str], PendingTicket]
ReadTicket = Callable[[], str]


class TicketWatcher:
    """Parse debounced edits, retaining a prior valid pending entry on parse failure."""

    def __init__(self, scheduler: Scheduler, parse: Parse, journal: JournalWriter, sleep: Sleep, *, debounce: float) -> None:
        self._scheduler = scheduler
        self._parse = parse
        self._journal = journal
        self._sleep = sleep
        self._debounce = debounce
        self._versions: dict[str, int] = {}

    async def changed(self, stem: str, read: ReadTicket) -> bool:
        """Observe one edit; superseded edits do not parse or affect the pending queue."""
        version = self._versions.get(stem, 0) + 1
        self._versions[stem] = version
        await self._sleep(self._debounce)
        if self._versions[stem] != version:
            return False
        try:
            ticket = self._parse(stem, read())
        except Exception as exc:
            self._journal.append(EventType.SIGNAL, {"signal": "ticket_parse_failed", "error": str(exc)}, ticket=stem)
            return False
        self._scheduler.consider(ticket)
        return True
