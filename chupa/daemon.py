"""Production daemon core and dispatch ownership (CHUPA_PLAN.md 19.P3.scheduler-activation)."""

import asyncio
from collections.abc import Callable, Set
from dataclasses import dataclass
from pathlib import Path

from chupa.config import Config, ConfigSnapshot, snapshot_config
from chupa.journal import Journal
from chupa.runner import Dispatch
from chupa.scheduler import Scheduler
from chupa.seams import Clock, Sleep
from chupa.tickets import Ticket
from chupa.watcher import Watcher


@dataclass(frozen=True)
class DaemonCore:
    admission: "DaemonAdmission"
    scheduler: Scheduler
    watcher: Watcher


def daemon_core(
    repo: Path, *, journal: Journal, load: Callable[[], Config],
    bind: Callable[[ConfigSnapshot], Dispatch], plan: str | None,
    read: Callable[[str], str | None], clock: Clock, sleep: Sleep, debounce: float,
    quarantined: Callable[[], Set[str]], drought_parked: Callable[[], Set[str]],
    completed_unmerged: Callable[[], int], max_unmerged: int,
) -> DaemonCore:
    admission = DaemonAdmission(snapshot_dispatch(load, bind))
    scheduler = Scheduler(
        journal, admission.dispatch, quarantined=quarantined, drought_parked=drought_parked,
        completed_unmerged=completed_unmerged, max_unmerged=max_unmerged,
    )
    watcher = Watcher(
        repo, journal=journal, plan=plan, read=read, publish=scheduler.update, remove=scheduler.remove,
        clock=clock, sleep=sleep, debounce=debounce,
    )
    return DaemonCore(admission, scheduler, watcher)


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
