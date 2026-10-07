"""Dormant dispatch task ownership (CHUPA_PLAN.md 19.P3.dispatch-admission-boundary)."""

import asyncio

from chupa.runner import Dispatch
from chupa.tickets import Ticket


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
