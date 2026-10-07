"""Dormant dispatch task ownership (CHUPA_PLAN.md 19.P3.dispatch-admission-boundary)."""

import asyncio
from collections.abc import Callable

from chupa.config import Config, ConfigSnapshot, snapshot_config
from chupa.runner import Dispatch
from chupa.tickets import Ticket


def snapshot_dispatch(load: Callable[[], Config], bind: Callable[[ConfigSnapshot], Dispatch]) -> Dispatch:
    """Bind a fresh snapshot inside the admission-owned callback's lifetime, never while queued."""
    async def dispatch(ticket: Ticket) -> str:
        snapshot = snapshot_config(load())
        callback = bind(snapshot)
        return await callback(ticket)

    return dispatch


class DaemonAdmission:
    def __init__(self, dispatch: Dispatch) -> None:
        self._dispatch = dispatch
        self._slot = asyncio.Lock()
        self.active: Ticket | None = None
        self.task: asyncio.Task[str] | None = None

    async def dispatch(self, ticket: Ticket) -> str:
        async with self._slot:
            async def invoke() -> str:
                return await self._dispatch(ticket)

            task = asyncio.create_task(invoke())
            self.active, self.task = ticket, task
            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                task.cancel()
                # Repeated caller cancellation must not interrupt the callback's cleanup.
                while not task.done():
                    try:
                        await asyncio.shield(task)
                    except asyncio.CancelledError:
                        pass
                    except Exception:
                        break
                if not task.cancelled():
                    task.exception()
                raise
            finally:
                self.active, self.task = None, None
