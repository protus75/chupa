"""Continuous foreground lifetime (CHUPA_PLAN.md 19.P3.serve-activation)."""

import asyncio
import re
from collections.abc import Awaitable, Callable, Iterable
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

from chupa import runner, triage
from chupa.config import ConfigError, snapshot_config
from chupa.daemon import DaemonTasks, HeartbeatCycle, TicketWriter, WorkerFailureObserver, WorkerStop, _protected_cleanup, _stop_workers, checkpoint_push
from chupa.drain import reexec_argv
from chupa.effects import Effects
from chupa.enginelog import EngineLog
from chupa.git import GitError
from chupa.heartbeat import Heartbeat
from chupa.journal import EventType, JournalCorruption, run_seq
from chupa.lockfile import Lockfile
from chupa.merge import AdmissionBoundary
from chupa.mergequeue import ConflictHandoff, regate_receipts
from chupa.providers import ProviderLLM, ProviderSetupError
from chupa.redact import Redactor
from chupa.seams import ExecutableNotFound, SubprocessExec
from chupa.stages import ticket_blob
from chupa.storm import StormLedger
from chupa.tickets import Ticket, TicketInvalid, intake, parse_ticket, ticket_path

SERVE_POLL_S = 0.1


class Responsiveness:
    """A round trip through an owned consumer, independent of task existence."""

    def __init__(self) -> None:
        self.request = asyncio.Event()
        self.sent = self.answered = 0

    def ask(self) -> None:
        self.sent += 1
        self.request.set()

    def reply(self) -> None:
        self.answered = self.sent
        self.request.clear()

    def responsive(self) -> bool:
        return self.sent > 0 and self.answered == self.sent

    async def wait(self, work: Awaitable):
        """The consumer stays responsive while owning and awaiting its operation."""
        task = asyncio.ensure_future(work)
        ping = None
        try:
            while not task.done():
                ping = asyncio.create_task(self.request.wait())
                await asyncio.wait((task, ping), return_when=asyncio.FIRST_COMPLETED)
                if ping.done():
                    self.reply()
                else:
                    ping.cancel()
                await asyncio.gather(ping, return_exceptions=True)
            return task.result()
        finally:
            if ping is not None:
                ping.cancel()
                await asyncio.gather(ping, return_exceptions=True)
            if not task.done():
                task.cancel()
            await _protected_cleanup(asyncio.gather(task, return_exceptions=True))


class Serve:
    """One idle composition; only run acquires the lock and starts owned work."""

    def __init__(
        self,
        checkout: runner.Checkout,
        *,
        config_path: Path | None = None,
        read: Callable[[str], str | None],
        stems: Callable[[], Iterable[str]],
        prepare=runner.prepare_pipeline,
        signals: Callable | None = None,
        failure: Callable[[BaseException], None] | None = None,
        argv=("serve",),
        reexec=None,
    ) -> None:
        from chupa.__main__ import build_daemon_core, build_notifications

        self.argv, self.reexec = tuple(argv), reexec or SubprocessExec()
        self.engine = Path(__file__).resolve().parent.parent
        self.trees = self.upgrade = None
        self.read, self.stems, self.signals = read, stems, signals
        self.prepare = prepare
        self.config_path = config_path
        self.writers: dict[str, TicketWriter] = {}
        self.published: dict[str, tuple[Ticket, str]] = {}
        self.queue = None
        self.stopping = False
        self.wake = asyncio.Event()
        self.ready = asyncio.Event()
        self.workers: tuple[asyncio.Task, ...] = ()
        self.health_tasks: tuple[asyncio.Task, ...] = ()
        self.mutating: asyncio.Task | None = None
        self.background: asyncio.Task | None = None
        self.observation: asyncio.Task | None = None
        self.stopper = self.observer = self.checkpoint = None
        self.responses = tuple(Responsiveness() for _ in range(4))
        self.log = EngineLog(checkout.config.state_dir / "engine.log", Redactor.from_config(checkout.config, checkout.env), checkout.clock)
        self.failure = failure or (lambda exc: self.log.event("worker_failure", error=str(exc)))
        self.notifications = build_notifications(checkout, config_path=config_path, log=self.log)

        async def prepared(local):
            callback = await prepare(local)
            if not isinstance(callback, TicketWriter):
                raise TypeError("serve preparation must return the composed TicketWriter")
            callback.ctx.boundary.select = self.select
            if self.queue is None:
                self.queue = callback.queue
            callback.queue = self.queue
            callback.admission = AdmissionBoundary(callback.ctx, mode="daemon", queue=self.queue, waiting=self.core.admission.waiting_for_merge)

            async def dispatch(ticket):
                if not self.select(ticket, "implement"):
                    self.core.scheduler.update(ticket)
                    return "running"
                try:
                    sha = await local.git.rev_parse(local.repo, f"main:{ticket_path(ticket.stem)}")
                    committed = await local.git._run(local.repo, "show", f"main:{ticket_path(ticket.stem)}")
                except GitError:
                    self.core.scheduler.update(ticket)
                    return "running"
                published = self.published.get(ticket.stem)
                if published is not None and published[0] is ticket and published[1] != sha:
                    try:
                        fresh = parse_ticket(ticket.stem, committed, local.repo)
                    except TicketInvalid:
                        return "running"
                    self.publish(fresh, committed)
                    return "running"
                self.writers[ticket.stem] = callback
                local.journal.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": sha}, ticket=ticket.stem, key=None)
                try:
                    return await callback(ticket)
                finally:
                    latest = next((e.body for e in reversed(local.journal.read()) if e.type == EventType.STATE_TRANSITION and e.ticket == ticket.stem), {})
                    if "provider_drought" in latest:
                        self.core.scheduler.update(ticket)
                    if not callback.continuations and not any(context is callback.ctx and stem in callback.queue.pending.keys() for stem, context in callback.queue.contexts.items()):
                        self.writers.pop(ticket.stem, None)

            return dispatch

        self.core = build_daemon_core(
            checkout,
            config_path=config_path,
                read=read,
            debounce=SERVE_POLL_S,
            quarantined=lambda: set(),
            drought_parked=lambda: set(),
            completed_unmerged=lambda: len(self.queue.pending) if self.queue is not None else 0,
            prepare=prepared,
        )
        publication: dict[str, str] = {}

        def watched_read(stem):
            text = self.read(stem)
            if text is not None:
                publication[stem] = text
            return text

        def watched_publish(ticket):
            self.publish(ticket, publication.pop(ticket.stem))

        self.core.watcher.read = watched_read
        self.core.watcher.publish = watched_publish
        self.checkout = replace(checkout, control=self.core.control)
        self.control = self.core.control
        assert self.control is not None and self.core.restart is not None
        self.control.inbox.draft = lambda stem: runner.committed_draft(self.checkout, stem)
        self.core.restart.admissions = self.reconstruct_admissions
        self.box = self.control._recover.__self__
        self.storm = StormLedger(journal=checkout.journal, clock=checkout.clock)
        self.core.scheduler.continuations = lambda: (c.ticket for w in self.writers.values() for c in w.continuations.values())
        self.core.scheduler.next_stage = self.next_stage
        self.core.scheduler.select = self.select
        self.core.admission.resume = self.resume
        self.core.restart.owned = lambda: self.core.admission.active is not None or self.core.admission.task is not None or any(w.continuations for w in self.writers.values())
        self.tasks = DaemonTasks(watcher=self.watch, merge_queue=self.merge, box_consumer=self.triage)
        self.heartbeat = HeartbeatCycle(
            heartbeat=Heartbeat(state_dir=checkout.config.state_dir, fs=checkout.fs),
            workers=lambda: self.healthy(0),
            merge_queue=lambda: self.healthy(1),
            box_consumer=lambda: self.healthy(2),
            watcher=lambda: self.healthy(3),
        )

    def publish(self, ticket: Ticket, text: str) -> None:
        self.published[ticket.stem] = ticket, ticket_blob(text.encode())
        self.core.scheduler.update(ticket)

    async def reconstruct_admissions(self):
        events = self.checkout.journal.read()
        receipts = regate_receipts(events)
        retained = {(r["stem"], r["attempt"]): r for r in receipts.values() if r["admission"] == "HELD"}
        live = [r for (stem, attempt), r in retained.items() if run_seq(events, stem) == attempt]
        if not live:
            return
        writer = runner.bind(self.checkout, None)
        self.queue = writer.queue
        writer.admission = AdmissionBoundary(writer.ctx, mode="daemon", queue=self.queue)
        for receipt in live:
            stem = receipt["stem"]
            ticket = await self.queue.retained_ticket(stem, receipt)
            self.queue.offer(ticket, attempt=receipt["attempt"])
            self.writers[stem] = writer

    def healthy(self, component: int) -> bool:
        return bool(self.health_tasks) and not self.health_tasks[component].done() and self.responses[component].responsive()

    def stop(self) -> None:
        self.stopping = True
        self.wake.set()

    def select(self, ticket: Ticket, stage: str) -> bool:
        self.control.poll()
        projection = self.control.projection
        if projection.kill_requested:
            self.stop()
        if ticket.stem not in self.writers and not self.stopping and self.control.providers.active:
            from chupa.config import load_config

            snapshot = load_config(self.config_path, cwd=self.checkout.repo)
            tier, _ = runner.capability(ticket, self.checkout.journal.read())
            drought = self.control.providers.drought(snapshot, tier, "implement")
            if drought:
                self.control.providers.park(ticket.stem, drought)
                return False
        return (
            not self.stopping
            and (self.upgrade is None and not projection.stop_requested or ticket.stem in self.writers)
            and projection.pause_id is None
            and (self.control.admission is None or self.control.admission in projection.released_hold_ids)
            and not any(target["emitting_origin"] == ticket.stem and target["emitting_stage"] == stage for target in self.storm.held_stages().values())
        )

    def next_stage(self, ticket: Ticket) -> str:
        writer = self.writers.get(ticket.stem)
        prior = writer.continuations.get(ticket.stem) if writer is not None else None
        return prior.next_stage if prior is not None else "implement"

    def resume(self, ticket: Ticket):
        writer = self.writers.get(ticket.stem)
        return writer if writer is not None and ticket.stem in writer.continuations else None

    @asynccontextmanager
    async def mutations(self):
        async with self.core.admission._slot:
            self.mutating = asyncio.current_task()
            try:
                yield
            finally:
                self.mutating = None

    async def scan(self) -> dict[str, str | None]:
        async with self.mutations():
            if self.stopping:
                return {}
            c = self.checkout
            await intake(c.repo, c.git, c.journal, c.fs)
            return {stem: self.read(stem) for stem in self.stems()}

    async def watch(self) -> None:
        response = self.responses[3]

        async def changes():
            previous = {}
            while True:
                current = await response.wait(self.scan())
                # Hold admission through parsing/publication, including debounce unwind.
                await response.wait(self.core.admission._slot.acquire())
                try:
                    for stem in sorted(previous.keys() | current.keys()):
                        if stem not in previous or previous.get(stem) != current.get(stem):
                            yield stem
                    await response.wait(asyncio.gather(*self.core.watcher._waits.values()))
                finally:
                    self.core.admission._slot.release()
                previous = current
                await response.wait(self.checkout.sleep(SERVE_POLL_S))

        await self.core.watcher.run(changes())

    async def engine_trees(self):
        output = await self.checkout.git._run(self.engine, "rev-parse", "HEAD:chupa", "HEAD:specs")
        trees = output.splitlines()
        if len(trees) != 2 or any(re.fullmatch(r"[0-9a-f]{40,64}", tree) is None for tree in trees):
            raise ValueError("engine tree ids unavailable")
        return tuple(trees)

    async def check_upgrade(self):
        if self.trees is not None and self.upgrade is None:
            try:
                trees = await self.engine_trees()
            except GitError, ValueError, OSError:
                self.trees = None
                self.log.event("self_upgrade_off", reason="engine checkout tree ids unavailable")
                return
            if trees != self.trees:
                self.upgrade = trees

    def upgrade_idle(self):
        return (
            self.mutating is None
            and self.core.scheduler.active is None
            and self.core.admission.active is None
            and self.core.admission.task is None
            and not any(w.active or w.continuations for w in self.writers.values())
            and (self.queue is None or not self.queue.pending and self.queue.active is None)
        )

    async def dispatch(self) -> None:
        response = self.responses[0]
        while True:
            self.control.poll()
            if self.control.projection.kill_requested:
                self.stop()
            if not self.stopping and self.control.projection.pause_id is None and not self.core.admission._slot.locked():
                await response.wait(self.check_upgrade())
                await response.wait(self.core.scheduler.dispatch_next())
            await response.wait(self.checkout.sleep(SERVE_POLL_S))

    async def merge(self) -> None:
        response = self.responses[1]

        async def poll():
            async with self.mutations():
                self.control.poll()
                if self.stopping or self.control.projection.kill_requested:
                    return
                if self.queue is None:

                    async def confirm_draft(stem, request_id):
                        await runner.confirm_draft(stem, request_id, runner.bind(self.checkout, None).ctx)

                    await self.control.inbox.settle_admissions(confirm_draft)
                    return
                await self.control.inbox.settle_admissions(self.queue.confirm_draft)
                self.queue.deliveries = []
                await self.queue.process()
                for ticket, attempt, result in self.queue.deliveries:
                    owner = self.writers.get(ticket.stem) or next(w for w in self.writers.values() if w.ctx is self.queue.contexts.get(ticket.stem))
                    if isinstance(result, ConflictHandoff) and owner.ctx.driver.llm is None:
                        owner = await self.prepare(self.checkout)
                        owner.queue = self.queue
                        owner.ctx.boundary.select = self.select
                        owner.admission = AdmissionBoundary(owner.ctx, mode="daemon", queue=self.queue)
                    self.writers[ticket.stem] = owner
                    await owner.consume_result(ticket, result, attempt=attempt)
                    if ticket.stem not in self.queue.pending:
                        self.queue.contexts.pop(ticket.stem, None)
                await self.check_upgrade()
                for stem, writer in tuple(self.writers.items()):
                    if not writer.active and not writer.continuations and stem not in self.queue.pending:
                        del self.writers[stem]

        while True:
            await response.wait(poll())
            await response.wait(self.checkout.sleep(SERVE_POLL_S))

    async def triage(self) -> None:
        response = self.responses[2]

        async def poll():
            async with self.mutations():
                if self.stopping:
                    return
                c = replace(self.checkout, config=snapshot_config(self.control.load_config()))
                triage.report_intake(c)
                if not self.box.pending():
                    return
                llm = ProviderLLM(c.config, exec_=c.exec_, fs=c.fs, env=c.env, cwd=c.repo, timeout=runner.call_timeout(c.config), session=self.control.providers)
                problems = await llm.preflight() if self.control.providers.active else []
                if problems:
                    raise ProviderSetupError("; ".join(problems))
                await triage.triage_pass(c, llm)

        while True:
            await response.wait(poll())
            await response.wait(self.checkout.sleep(SERVE_POLL_S))

    async def abort(self) -> None:
        operations = {task for task in (self.core.admission.task, self.mutating) if task is not None}
        aborts = [writer.abort_current for writer in tuple(self.writers.values())]
        if self.control.author_driver is not None:
            aborts.append(self.control.author_driver.abort_current)
        errors = []
        for abort in aborts:
            try:
                await abort()
            except BaseException as exc:
                errors.append(exc)
        # Observe preparation and non-model process operations before WorkerStop touches workers.
        for task in operations:
            if not task.done() and not task.cancelling():
                task.cancel()
        for task in operations:
            cleanup = asyncio.gather(task, return_exceptions=True)
            await _protected_cleanup(cleanup)
            errors.extend(result for result in cleanup.result() if isinstance(result, BaseException) and not isinstance(result, asyncio.CancelledError))
        if errors:
            raise errors[0]

    async def cleanup(self) -> None:
        await self.ready.wait()
        abort_error = None
        try:
            await self.stopper.stop(replace(self.control.projection, kill_requested=True))
        except BaseException as exc:
            abort_error = exc
        finally:
            # Even a failed abort has unwound before worker cleanup. It cannot earn kill_applied.
            await _protected_cleanup(_stop_workers(self.workers))
            await _protected_cleanup(asyncio.create_task(self.notifications.close()))
        results = await asyncio.gather(self.background, self.observation, return_exceptions=True)
        errors = [task.exception() for task in self.workers if not task.cancelled()]
        errors += [r for r in results if isinstance(r, BaseException)]
        for writer in self.writers.values():
            writer.continuations.clear()
        if abort_error is not None:
            raise abort_error
        for error in errors:
            if isinstance(error, BaseException) and not isinstance(error, asyncio.CancelledError):
                raise error

    async def maintenance(self) -> None:
        self.control.poll()
        if self.control.projection.kill_requested:
            self.stop()
        if self.stopping:
            return
        self.core.restart.timers.fire_due()
        if not self.core.admission._slot.locked() and not self.core.scheduler._slot.locked():
            await self.core.sweep_orphans()
            async with self.core.admission._slot:
                self.box.recover()
                await self.checkpoint.poll()
        self.heartbeat.cycle()
        self.notifications.poll()

    async def run(self) -> int:
        c = self.checkout
        lock = Lockfile(c.config.state_dir, instance_id=await c.git.describe(c.repo), clock=c.clock)
        lock.acquire()

        def restore():
            return None

        code = 0
        upgrade_stop = False
        try:
            try:
                try:
                    self.trees = await self.engine_trees()
                except Exception:
                    self.log.event("self_upgrade_off", reason="engine checkout tree ids unavailable")
                await self.core.startup()
                self.notifications.poll(startup=True)
            except Exception as exc:
                raise runner.Refusal(f"serve startup recovery refused: {exc}", "repair the recovery evidence and start serve again") from exc
            self.control.publish()
            if self.signals is not None:
                restore = self.signals(self.stop)
            self.checkpoint = checkpoint_push(c.repo, journal=c.journal, effects=Effects(c.journal), timers=self.core.restart.timers, git=c.git, box=self.box, clock=c.clock, log=self.log)
            # Guard only this lifetime: the component's ordinary run semantics stay intact.
            pending_failure = None

            async def guarded(callback):
                nonlocal pending_failure, code
                try:
                    await callback()
                    raise RuntimeError("owned serve consumer returned unexpectedly")
                except BaseException as exc:
                    # Latch before DaemonTasks cancels siblings; those cancellations
                    # belong to this lifetime's cleanup, not another worker failure.
                    if not self.stopping and not self.control.projection.kill_requested:
                        pending_failure = exc
                        code = 2 if isinstance(exc, (ConfigError, runner.Refusal, ProviderSetupError, JournalCorruption, ExecutableNotFound)) else 1
                    self.stop()
                    raise

            def observed_failure(_exc):
                nonlocal pending_failure
                if pending_failure is not None:
                    exc, pending_failure = pending_failure, None
                    self.failure(exc)

            self.tasks._consumers = tuple((lambda callback=callback: guarded(callback)) for callback in self.tasks._consumers)

            def bind(tasks):
                self.workers = (worker, *tasks)
                self.health_tasks = (worker, tasks[1], tasks[2], tasks[0])
                self.stopper = WorkerStop(lifecycle_id=self.control.projection.lifecycle_id, abort=self.abort, workers=self.workers)
                self.observer = WorkerFailureObserver(lifecycle_id=self.control.projection.lifecycle_id, workers=self.workers, projection=lambda: self.control.projection, failure=observed_failure)
                self.observation = asyncio.create_task(self.observer.observe())
                self.ready.set()

            self.tasks.started = bind
            self.background = asyncio.create_task(self.tasks.run())
            worker = asyncio.create_task(guarded(self.dispatch))
            try:
                await self.ready.wait()
                while not self.stopping:
                    await self.maintenance()
                    if (self.upgrade is not None or self.control.projection.stop_requested) and self.upgrade_idle() and not self.stopping:
                        self.control.poll()
                        if self.control.projection.kill_requested:
                            self.stop()
                        else:
                            upgrade_stop = not self.control.projection.stop_requested
                            self.stop()
                            break
                    for response in self.responses:
                        response.ask()
                    done = [task for task in self.workers if task.done()]
                    if done:
                        for task in done:
                            if task.cancelled():
                                raise RuntimeError("owned serve consumer cancelled unexpectedly")
                            task.result()
                        raise RuntimeError("owned serve consumer stopped unexpectedly")
                    sleeping = asyncio.create_task(c.sleep(SERVE_POLL_S))
                    stopping = asyncio.create_task(self.wake.wait())
                    try:
                        await asyncio.wait((sleeping, stopping), return_when=asyncio.FIRST_COMPLETED)
                    finally:
                        sleeping.cancel()
                        stopping.cancel()
                        await _protected_cleanup(asyncio.gather(sleeping, stopping, return_exceptions=True))
            except asyncio.CancelledError:
                self.stop()
            except Exception as exc:
                self.log.event("serve_failed", error=str(exc))
                code = 2 if isinstance(exc, (ConfigError, runner.Refusal, ProviderSetupError, JournalCorruption, ExecutableNotFound)) else 1
                self.stop()
            self.control.poll()
            handoff = upgrade_stop and self.upgrade is not None and self.upgrade_idle() and not self.control.projection.kill_requested and code == 0
            if handoff:
                c.journal.append(EventType.SIGNAL, {"signal": "serve_handoff", "chupa": self.upgrade[0], "specs": self.upgrade[1]})
            cleanup = asyncio.create_task(self.control.apply_kill(self.cleanup) if self.control.projection.kill_requested else self.cleanup())
            try:
                await _protected_cleanup(cleanup)
            except asyncio.CancelledError:
                if cleanup.cancelled():
                    code = 1
            except Exception as exc:
                self.log.event("serve_cleanup_failed", error=str(exc))
                if code != 2:
                    code = 1
            self.control.poll()
            handoff = handoff and not self.control.projection.kill_requested and not self.control.projection.stop_requested and code == 0
            if handoff:
                c.journal.close()
        finally:
            try:
                await _protected_cleanup(asyncio.create_task(self.notifications.close()))
                await _protected_cleanup(asyncio.create_task(self.control.providers.close()))
            finally:
                try:
                    self.control.retire()
                finally:
                    restore()
                    lock.release()
        if handoff:
            code, _, _ = await self.reexec.run(reexec_argv(self.argv, engine=self.engine), cwd=c.repo, env=c.env, timeout=None)
        return code


async def serve(
    checkout: runner.Checkout,
    *,
    config_path: Path | None = None,
    read: Callable[[str], str | None] | None = None,
    stems: Callable[[], Iterable[str]] | None = None,
    prepare=runner.prepare_pipeline,
    signals: Callable | None = None,
    failure: Callable[[BaseException], None] | None = None,
    argv=("serve",),
    reexec=None,
) -> int:
    from chupa.__main__ import build_serve

    owner = build_serve(checkout, config_path=config_path, read=read, stems=stems, prepare=prepare, signals=signals, failure=failure, argv=argv, reexec=reexec)
    return await owner.run()
