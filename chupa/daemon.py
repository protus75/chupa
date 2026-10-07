"""Production daemon core and dispatch ownership (CHUPA_PLAN.md 19.P3.scheduler-activation)."""

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Set
from dataclasses import dataclass
from pathlib import Path

from chupa.config import Config, ConfigSnapshot, snapshot_config
from chupa.control import ControlInbox, ControlProjection, write_active
from chupa.journal import Journal
from chupa import runner
from chupa.artifacts import Cost, Finding, StageResult
from chupa.caps import spent
from chupa.mergequeue import ConflictHandoff, MergeQueue
from chupa.rework import ReworkOrder, record_supersedes, rework
from chupa.runner import Dispatch
from chupa.scheduler import Scheduler
from chupa.seams import Clock, FileSystem, Sleep
from chupa.stages import StageContext
from chupa.tickets import Ticket, parse_ticket, ticket_path
from chupa.watcher import Watcher


def control_inbox(*, journal: Journal, lifecycle_id: str, holds: Callable[[], Set[str]],
                  apply: Callable[[ControlProjection], None],
                  files: Callable[[], Iterable[Path]], read: Callable[[Path], bytes]) -> ControlInbox:
    """Explicitly supplied by the lock holder, never a second writer."""
    return ControlInbox(journal=journal, lifecycle_id=lifecycle_id, holds=holds,
                        apply=apply, files=files, read=read)


class PauseConsumer:
    """One serial inbox and desired pause state, owned by the engine's writer lock."""

    def __init__(self, *, journal: Journal, lifecycle_id: str, state_dir: Path,
                 fs: FileSystem, sleep: Sleep, files: Callable[[], Iterable[Path]],
                 read: Callable[[Path], bytes]) -> None:
        self.state_dir, self.fs, self.sleep = state_dir, fs, sleep
        self.projection = ControlProjection(lifecycle_id)
        self._published = False
        self.inbox = control_inbox(journal=journal, lifecycle_id=lifecycle_id,
                                   holds=lambda: set(), apply=self._apply, files=files, read=read)

    def _apply(self, projection: ControlProjection) -> None:
        # The inbox has already fsynced the decision; discovery is only its projection.
        self.projection = projection
        if self._published:
            write_active(self.state_dir, projection, self.fs)

    def publish(self) -> None:
        self._published = True
        write_active(self.state_dir, self.projection, self.fs)

    def retire(self) -> None:
        write_active(self.state_dir, None, self.fs)
        self._published = False

    async def checkpoint(self) -> None:
        while True:
            self.inbox.consume()
            if self.projection.pause_id is None:
                return
            await self.sleep(0.1)


@dataclass(frozen=True)
class DaemonCore:
    admission: "DaemonAdmission"
    scheduler: Scheduler
    watcher: Watcher
    control: PauseConsumer | None = None


class DaemonTasks:
    """Explicit lifetime owner for dormant background consumers (19.P3.background-consumers)."""

    def __init__(self, *, watcher: Callable[[], Awaitable[object]],
                 merge_queue: Callable[[], Awaitable[object]],
                 box_consumer: Callable[[], Awaitable[object]]) -> None:
        self._consumers = (watcher, merge_queue, box_consumer)
        self.tasks: tuple[asyncio.Task, ...] = ()

    async def run(self) -> None:
        if self.tasks:
            raise ValueError("finish or cancel and await the existing DaemonTasks.run before another run")

        async def invoke(callback: Callable[[], Awaitable[object]]) -> None:
            await callback()

        self.tasks = tuple(asyncio.create_task(invoke(callback)) for callback in self._consumers)
        try:
            # Shield prevents owner cancellation from cancelling a consumer again during unwind.
            await asyncio.shield(asyncio.gather(*self.tasks))
        finally:
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            cleanup = asyncio.gather(*self.tasks, return_exceptions=True)
            cancelled = None
            while not cleanup.done():
                try:
                    await asyncio.shield(cleanup)
                except asyncio.CancelledError as exc:
                    cancelled = exc
            cleanup.result()
            self.tasks = ()
            if cancelled is not None:
                raise cancelled


async def apply_rework(ctx: StageContext, ticket: Ticket, findings: list[Finding], *, attempt: int,
                       handoff: ConflictHandoff | None = None) -> StageResult:
    """Publish exact reviewed proposals on the ticket plane under the caller's writer lock."""
    road = "shrink or split the committed ticket text and rerun drain"
    workspace = ctx.worktree(ticket.stem)
    if not workspace.exists():
        return StageResult(outcome="gate_failed", artifact=None, cost=Cost(), findings=[Finding(
            code="ticket_schema", message="Rework has no usable workspace", paved_road=road)])
    try:
        text = await ctx.git._run(ctx.repo, "show", f"HEAD:{ticket_path(ticket.stem)}")
        original = parse_ticket(ticket.stem, text, ctx.repo,
                                plan=(ctx.repo / "CHUPA_PLAN.md").read_text())
        tier, effort = runner.capability(original, ctx.driver.journal.read())
        result = await rework(ctx, original, text, findings, attempt=attempt, workspace=workspace,
                              tier=tier, effort=effort, stuck_budget=original.stuck_minutes * 60,
                              handoff=handoff)
        if result.outcome != "ok":
            return result
        order = result.artifact
        assert isinstance(order, ReworkOrder)
        if order.action == "escalate":
            return result
        paths = [ticket_path(p.stem) for p in order.tickets]
        before = await ctx.git.rev_parse(ctx.repo, "HEAD")

        async def restore_publication() -> None:
            # Restore also removes added successors from the index and worktree. Stage any
            # files left by a write/add failure so they belong to that same restore lane.
            written = [path for path in paths if (ctx.repo / path).is_file()]
            if written:
                await ctx.git.add(ctx.repo, written)
            indexed = set(await ctx.git.ls_files(ctx.repo))
            restorable = [path for path in paths if path in indexed]
            if restorable:
                await ctx.git.restore(ctx.repo, restorable, source=before)
            # A commit can land before its caller fails or exact-byte verification refuses.
            # Compensate only its proposal paths, preserving unrelated staged work.
            committed = (await ctx.git._run(
                ctx.repo, "diff", "--name-only", before, "HEAD", "--", *paths)).splitlines()
            if committed:
                await ctx.git.commit(ctx.repo, f"chupa({ticket.stem}): undo refused rework", only=committed)

        async def publish() -> dict:
            for proposal, path in zip(order.tickets, paths, strict=True):
                ctx.fs.write(ctx.repo / path, proposal.ticket.encode())
            await ctx.git.add(ctx.repo, paths)
            await ctx.git.commit(ctx.repo, f"chupa({ticket.stem}): rework", only=paths)
            for proposal, path in zip(order.tickets, paths, strict=True):
                if await ctx.git._run(ctx.repo, "show", f"HEAD:{path}") != proposal.ticket:
                    raise ValueError(f"committed {path} differs from the reviewed proposal")
            return {"commit": await ctx.git.rev_parse(ctx.repo, "HEAD")}

        try:
            await ctx.driver.effects.run(publish, key=f"ticket-plane/{ticket.stem}/{attempt}/rework",
                                         ticket=ticket.stem)
            if errors := await record_supersedes(ctx, order):
                await restore_publication()
                return StageResult(outcome="gate_failed", artifact=None, cost=result.cost, findings=errors)
        except BaseException:
            cleanup = asyncio.create_task(restore_publication())
            try:
                await asyncio.shield(cleanup)
            except asyncio.CancelledError:
                await cleanup
                raise
            raise
        return result
    except Exception as exc:
        return StageResult(outcome="gate_failed", artifact=None, cost=Cost(), findings=[Finding(
            code="ticket_schema", message=ctx.driver.redactor.scrub(f"Rework publication refused: {exc}"),
            paved_road="commit every exact reviewed proposal before supersession; " + road)])


class TicketWriter:
    """The composed ticket writer; queue handoffs are consumed only after admission unwinds."""

    def __init__(self, ctx: StageContext, queue: MergeQueue) -> None:
        self.ctx, self.queue = ctx, queue

    async def __call__(self, ticket: Ticket) -> str:
        return await runner.drive(self.ctx, ticket)

    async def consume_handoff(self, ticket: Ticket, handoff: ConflictHandoff, *, attempt: int) -> str:
        if self.queue.active is not None or self.queue._slot.locked():
            raise ValueError("finish and await MergeQueue.process before consuming its handoff")
        ctx = self.ctx
        outcome = "gate_failed"
        await runner.harvest_failure(ctx, ticket, attempt=attempt, stage="merge", outcome=outcome,
                                     findings=handoff.findings, results=())
        reply = None
        if not spent(ctx.config.caps, ctx.driver.journal.read(), ticket.stem):
            reply = await apply_rework(ctx, ticket, handoff.findings, attempt=attempt, handoff=handoff)
        return await runner.failure_terminal(ctx, ticket, outcome=outcome, stage="merge",
                                             findings=handoff.findings, attempt=attempt, reworked=reply,
                                             rework_requested=True)


def daemon_core(
    repo: Path, *, journal: Journal, load: Callable[[], Config],
    bind: Callable[[ConfigSnapshot], Dispatch], plan: str | None,
    read: Callable[[str], str | None], clock: Clock, sleep: Sleep, debounce: float,
    quarantined: Callable[[], Set[str]], drought_parked: Callable[[], Set[str]],
    completed_unmerged: Callable[[], int], max_unmerged: int,
    before_dispatch: Callable[[], Awaitable[None]] | None = None,
    control: PauseConsumer | None = None,
) -> DaemonCore:
    admission = DaemonAdmission(snapshot_dispatch(load, bind), before_dispatch=before_dispatch)
    scheduler = Scheduler(
        journal, admission.dispatch, quarantined=quarantined, drought_parked=drought_parked,
        completed_unmerged=completed_unmerged, max_unmerged=max_unmerged,
    )
    watcher = Watcher(
        repo, journal=journal, plan=plan, read=read, publish=scheduler.update, remove=scheduler.remove,
        clock=clock, sleep=sleep, debounce=debounce,
    )
    return DaemonCore(admission, scheduler, watcher, control)


def snapshot_dispatch(load: Callable[[], Config], bind: Callable[[ConfigSnapshot], Dispatch]) -> Dispatch:
    """Bind a fresh snapshot inside the admission-owned callback's lifetime, never while queued."""
    async def dispatch(ticket: Ticket) -> str:
        snapshot = snapshot_config(load())
        callback = bind(snapshot)
        return await callback(ticket)

    return dispatch


class DaemonAdmission:
    def __init__(self, dispatch: Dispatch, *,
                 before_dispatch: Callable[[], Awaitable[None]] | None = None) -> None:
        self._dispatch = dispatch
        self._before_dispatch = before_dispatch
        self._slot = asyncio.Lock()
        self.active: Ticket | None = None
        self.task: asyncio.Task[str] | None = None

    async def dispatch(self, ticket: Ticket) -> str:
        async with self._slot:
            if self._before_dispatch is not None:
                await self._before_dispatch()

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
