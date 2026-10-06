"""Dormant single-flight dispatch projection (CHUPA_PLAN.md 19.P3.daemon-scheduler)."""

import asyncio
from collections.abc import Awaitable, Callable, Set

from chupa.drain import SETTLED, authored_at, sort_key
from chupa.journal import Journal
from chupa.status import last_states, reject_queue
from chupa.tickets import Ticket


class Scheduler:
    def __init__(
        self, journal: Journal, dispatch: Callable[[Ticket], Awaitable[object]], *,
        quarantined: Callable[[], Set[str]], drought_parked: Callable[[], Set[str]],
        completed_unmerged: Callable[[], int], max_unmerged: int,
    ) -> None:
        self.journal = journal
        self.dispatch = dispatch
        self.quarantined = quarantined
        self.drought_parked = drought_parked
        self.completed_unmerged = completed_unmerged
        self.max_unmerged = max_unmerged
        self.pending: dict[str, Ticket] = {}
        self.active: Ticket | None = None
        self._slot = asyncio.Lock()

    def update(self, ticket: Ticket) -> None:
        self.pending[ticket.stem] = ticket

    def remove(self, stem: str) -> None:
        self.pending.pop(stem, None)

    async def dispatch_next(self) -> Ticket | None:
        """Concurrent requests wait for completion, then select from current projections."""
        async with self._slot:
            events = self.journal.read()
            last = last_states(events)
            held = set(reject_queue(events)) | self.quarantined() | self.drought_parked()
            if self.completed_unmerged() >= self.max_unmerged:
                return None
            authored = authored_at(events)
            ready = [t for t in self.pending.values()
                     if t.frontmatter.state == "confirmed"
                     and last.get(t.stem) not in SETTLED | {"rejected", "running"}
                     and t.stem not in held and all(last.get(d) in SETTLED for d in t.depends)]
            if not ready:
                return None
            ticket = min(ready, key=lambda t: sort_key(t, authored))
            self.remove(ticket.stem)
            self.active = ticket
            try:
                await self.dispatch(ticket)
            finally:
                self.active = None
            return ticket
