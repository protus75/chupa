"""Dormant single-flight scheduling (CHUPA_PLAN.md section 9).

This module deliberately has no production caller until scheduler activation.  It
keeps only the pending ordering and the one active dispatch; ticket discovery and
dependency eligibility remain the responsibility of the composition that calls it.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


@dataclass(frozen=True)
class PendingTicket:
    """The scheduler's complete ordering input for one eligible ticket."""

    stem: str
    priority: str
    authored_at: str | None


Dispatch = Callable[[PendingTicket], Awaitable[None]]


def sort_key(ticket: PendingTicket) -> tuple[int, bool, str, str]:
    """Priority first, then first authoring event, with stem as a stable final tie-break."""
    return (PRIORITY[ticket.priority], ticket.authored_at is None, ticket.authored_at or "", ticket.stem)


class Scheduler:
    """A one-slot dispatcher whose pending entries may be reordered while work runs."""

    def __init__(self, dispatch: Dispatch) -> None:
        self._dispatch = dispatch
        self._pending: dict[str, PendingTicket] = {}
        self.active: PendingTicket | None = None

    @property
    def pending(self) -> tuple[PendingTicket, ...]:
        return tuple(sorted(self._pending.values(), key=sort_key))

    def consider(self, ticket: PendingTicket) -> None:
        """Add or replace pending work; an active ticket is never preempted."""
        if self.active is None or ticket.stem != self.active.stem:
            self._pending[ticket.stem] = ticket

    def forget(self, stem: str) -> None:
        """Remove work that is no longer eligible."""
        self._pending.pop(stem, None)

    async def dispatch_one(self) -> PendingTicket | None:
        """Dispatch one ticket, or none when the single slot is already occupied or empty."""
        if self.active is not None or not self._pending:
            return None
        ticket = self.pending[0]
        del self._pending[ticket.stem]
        self.active = ticket
        try:
            await self._dispatch(ticket)
        finally:
            self.active = None
        return ticket
