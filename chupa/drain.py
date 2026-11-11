"""The `drain` scaffold verb: run the ready queue to quiescence.

One ticket at a time, in the one process holding the single-writer lock, through the same dispatch seam as
`run <stem>`. A non-ok terminal parks its stem and the drain moves on; at quiescence each parked stem with
`retry` budget left is re-offered, one journaled `cap_consumed` unit per re-offer, findings-fed: the Implement
render folds the prior terminal's durable findings into criteria-position. Every selection re-scans
the committed tickets dir and re-folds the journal, so a merge or a ticket-plane commit landed mid-invocation
is visible to the very next pick. This is the eligibility sort's owner.

In the engine's own source tree, an admission touching `chupa/**` (including `chupa/specs/**`) is a SELF-UPGRADE: before the next dispatch the drain hands off to
a re-exec'd child running the upgraded checkout, carrying the invocation's parked set in
argv. A `premise_failed` stem stays parked until its committed `ticket.md` changes.
"""

import asyncio
import json
import os
import sys
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from chupa import caps, control
from chupa.control import ControlRequest
from chupa.enginelog import EngineLog
from chupa.journal import TERMINAL_STATES, Event, EventType, render_ts
from chupa.lockfile import Lockfile
from chupa.reconcile import reconcile
from chupa.redact import Redactor
from chupa.runner import EXIT_MERGED, EXIT_TICKET, Checkout, Dispatch, Refusal, harvest_orphan
from chupa.seams import ProcessExec
from chupa.status import SETTLED, last_states, reject_queue
from chupa.tickets import (
    INTAKE_SIGNAL,
    TICKET_FILE,
    TICKETS_DIR,
    Ticket,
    TicketInvalid,
    _porcelain,
    depends_cycle,
    intake,
    parse_ticket,
    ticket_path,
)

ENGINE = Path(__file__).resolve().parent.parent

HALT_SIGNAL = "drain_halted"
CEILING = "drain.max_runtime_hours"
# A `rejected` stem is retired: never dispatched again.
RETIRED = frozenset({"rejected"})
PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

PREMISE = "premise_failed"
HANDOFF_SIGNAL = "drain_handoff"
# The engine plane the running process has loaded: admitting a change under either re-execs the drain.
UPGRADE_PREFIXES = ("chupa/",)


def reexec_argv(args: Iterable[str], *, engine: Path | None = None) -> list[str]:
    engine = ENGINE if engine is None else engine
    return ["uv", "run", "--project", str(engine), "python", "-m", "chupa", *args]


def parked_blob(events: Iterable[Event], stem: str) -> str | None:
    """Return the content identity held by the last transition, if any."""
    body: Mapping = {}
    ran_sha: str | None = None
    for e in events:
        if e.type == EventType.STATE_TRANSITION and e.ticket == stem:
            body = e.body
            if body.get("to") == "running":
                ran_sha = body.get("ticket_sha")
        elif (
            e.type == EventType.SIGNAL
            and e.ticket == stem
            and body.get("to") == PREMISE
            and e.body.get("signal") == "reject_verdict"
            and e.body.get("verdict") == "keep"
            and e.body.get("actor") == "operator"
        ):
            body = {}
    if body.get("to") == PREMISE or (body.get("to") == "gate_failed" and "diff_budget" in body.get("reason", "").split(",")):
        return ran_sha
    return None


def awaiting_operator(events: Iterable[Event], stem: str, caps_config) -> bool:
    history = tuple(events)
    queued = reject_queue(history)
    return stem in queued and ("ticket_changed" in queued[stem].get("reason", "").split(",") or caps.spent(caps_config, history, stem) is not None)


def reofferable(events: Iterable[Event], stem: str, caps_config) -> bool:
    history = tuple(events)
    return not awaiting_operator(history, stem, caps_config) and caps.spent(caps_config, history, stem) is None


def record_reoffer(journal, events: Iterable[Event], stem: str, sha: str) -> None:
    history = tuple(events)
    if stem in reject_queue(history):
        journal.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, ticket=stem)
    body = next(e.body for e in reversed(history) if e.type == EventType.STATE_TRANSITION and e.ticket == stem and e.body.get("to") in TERMINAL_STATES)
    if body.get("to") != PREMISE and "provider_drought" not in body and not (body.get("to") in {"infra_error", "timeout"} and "rung" not in body):
        caps.consume(journal, stem, "retry", sha, rung=body.get("rung"))


def authored_at(events: Iterable[Event]) -> dict[str, str]:
    """Each stem's age anchor: the `ts` of its FIRST ticket-plane authoring-commit event."""
    first: dict[str, str] = {}
    for e in events:
        if e.type == EventType.SIGNAL and e.body.get("signal") == INTAKE_SIGNAL and e.ticket is not None:
            first.setdefault(e.ticket, e.ts)
    return first


def sort_key(ticket: Ticket, authored: Mapping[str, str]) -> tuple:
    """(priority, age, stem): older first; a stem with no authoring event has no seniority and sorts last."""
    ts = authored.get(ticket.stem)
    return (PRIORITY[ticket.frontmatter.priority], ts is None, ts or "", ticket.stem)


def order_tickets(tickets: Iterable[Ticket], authored: Mapping[str, str]) -> list[Ticket]:
    """Apply soft edges only within the eligible set, breaking ties by sort_key."""
    remaining = sorted(tickets, key=lambda t: sort_key(t, authored))
    ordered = []
    while remaining:
        named = {stem for ticket in remaining for stem in ticket.runs_before}
        # Malformed committed cycles must not stall dispatch.
        ticket = next((t for t in remaining if t.stem not in named), remaining[0])
        remaining.remove(ticket)
        ordered.append(ticket)
    return ordered


def write_queue(state_dir, fs, clock, ordered: list[Ticket]) -> None:
    value = {"at": render_ts(clock()), "order": [t.stem for t in ordered], "runs_before": {t.stem: list(t.runs_before) for t in ordered if t.runs_before}}
    fs.write(state_dir / "queue.json", (json.dumps(value) + "\n").encode())


@dataclass(frozen=True)
class Parked:
    stem: str
    reason: str
    paved_road: str
    findings: tuple[str, ...] = ()


@dataclass
class Report:
    merged: list[str] = field(default_factory=list)
    parked: list[Parked] = field(default_factory=list)
    blocked: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)
    unadmitted: list[str] = field(default_factory=list)  # eligible but never run: only a halt leaves any
    invalid: list[tuple[str, str]] = field(default_factory=list)
    drafts: list[str] = field(default_factory=list)
    halted: str | None = None
    handoff: int | None = None  # the re-exec'd child's exit code: the child reports, the parent stays silent
    killed: bool = False
    stopped: bool = False

    @property
    def exit_code(self) -> int:
        if self.handoff is not None:
            return self.handoff
        # Quiescence is 0 whatever it parked; a ceiling halt is a non-quiescent stop.
        return EXIT_TICKET if self.halted or self.killed else EXIT_MERGED

    def render(self) -> str:
        def block(name: str, lines: Iterable[str]) -> str:
            return f"{name}:\n" + ("\n".join(f"- {line}" for line in lines) or "(none)")

        if self.killed:
            head = "drain stopped by kill -- NOT quiescent. Continue with `uv run python -m chupa drain`."
        elif self.stopped:
            head = "drain stopped on request; no new ticket was admitted."
        elif self.halted:
            head = f"drain HALTED by the {CEILING} ceiling ({self.halted}) -- NOT quiescent; no new ticket was admitted. Continue with `uv run python -m chupa drain`."
        elif not (self.merged or self.parked or self.blocked):
            head = "drain quiescent: nothing eligible (empty ready set)."
        else:
            head = "drain quiescent: nothing eligible, unparked, re-offerable, or newly authored."
        parked = (f"{p.stem}: {p.reason} -- {p.paved_road}" + "".join(f"\n  - {f}" for f in p.findings) for p in self.parked)
        return (
            "\n\n".join(
                (
                    head,
                    block("merged this invocation", self.merged),
                    block("parked", parked),
                    block("eligible, not admitted", self.unadmitted),
                    block("blocked on unmerged depends", (f"{s}: waits on {', '.join(d)}" for s, d in self.blocked)),
                    block("invalid committed tickets", (f"{s}: {why}" for s, why in self.invalid)),
                    block("drafts awaiting confirm", self.drafts),
                )
            )
            + "\n"
        )


@dataclass(frozen=True)
class _Scan:
    tickets: dict[str, Ticket]
    invalid: dict[str, str]
    drafts: tuple[str, ...]


async def drain(
    checkout: Checkout,
    dispatch: Dispatch,
    *,
    reexec: ProcessExec,
    parked: Iterable[str] = (),
    deadline: datetime | None = None,
    argv: Iterable[str] = ("drain",),
    before_dispatch: Callable[[], Awaitable[None]] | None = None,
    stop_lifecycle: str | None = None,
    signals: Callable[[Callable[[], None]], Callable[[], None]] | None = None,
) -> Report:
    """`reexec` is the handoff's own process seam: never the instance active work spawns through."""
    consumer = checkout.control
    if consumer is None:
        raise Refusal("admission control consumer absent", "construct it with `build_control` at the composition root and supply it as `Checkout.control`")
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    log = EngineLog(checkout.config.state_dir / "engine.log", Redactor.from_config(checkout.config, checkout.env), checkout.clock)
    pid = os.getpid()
    lock.acquire()
    outcome = "quiescent"
    restore = None
    try:
        log.event("engine_start", verb="drain", pid=pid)
        if stop_lifecycle is not None:
            consumer.inbox.lifecycle_id = stop_lifecycle
            consumer.inbox.recover()
        consumer.publish()

        async def control_checkpoint() -> None:
            if consumer.projection.stop_requested:
                return
            stopped = asyncio.Event()
            apply = consumer.inbox.apply

            def observe(projection) -> None:
                apply(projection)
                if projection.stop_requested:
                    stopped.set()

            consumer.inbox.apply = observe
            pending = asyncio.create_task(consumer.checkpoint())
            watcher = asyncio.create_task(stopped.wait())
            try:
                await asyncio.wait((pending, watcher), return_when=asyncio.FIRST_COMPLETED)
                if pending.done():
                    pending.result()
            finally:
                consumer.inbox.apply = apply
                for task in (pending, watcher):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(pending, watcher, return_exceptions=True)

        async def checkpoint() -> None:
            await control_checkpoint()
            if consumer.projection.kill_requested or consumer.projection.stop_requested:
                return
            if before_dispatch is not None:
                await before_dispatch()
            await control_checkpoint()

        assert checkout.config.worktree_root is not None  # resolved at config load
        await reconcile(checkout.journal, checkout.git, checkout.repo, checkout.config.worktree_root, lambda stem, attempt: harvest_orphan(checkout, stem, attempt))
        consumer.providers.timers.reconstruct()
        consumer.providers.timers.fire_due()
        if hasattr(dispatch, "prepare"):
            await dispatch.prepare()
        await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs)
        run = _Drain(checkout, dispatch, frozenset(parked), before_dispatch=checkpoint, deadline=deadline)
        if signals is not None:
            restore = signals(run._signal_kill)
        run.retro = getattr(dispatch, "_retro", None)
        report = await run.run()
        # A pending self-upgrade is still an offer boundary, never permission to
        # launch a child after a kill accepted during the final preparation.
        await control_checkpoint()
        if run._stopping():
            await consumer.apply_kill(dispatch.abort_current)
            report.killed = True
            outcome = "killed"
            return report
        if run.upgrade is None:
            report.stopped = consumer.projection.stop_requested
            outcome = "stopped" if report.stopped else "halted" if report.halted else "quiescent"
            return report
        stem, commit = run.upgrade
        carried = run.parked_stems()
        checkout.journal.append(EventType.SIGNAL, {"signal": HANDOFF_SIGNAL, "commit": commit, "parked": list(carried), "merged": list(report.merged)}, ticket=stem)
        checkout.journal.close()
        outcome = "handoff"
    finally:
        try:
            try:
                await consumer.providers.close()
            finally:
                consumer.retire()
        finally:
            try:
                exc = sys.exception()
                log.event("engine_stop", verb="drain", pid=pid, outcome=f"error: {type(exc).__name__}" if exc else outcome)
            finally:
                try:
                    if restore is not None:
                        restore()
                finally:
                    lock.release()
    # The fixed HANDOFF order: journaled, journal closed, lock free -- the child is the only writer,
    # and the parent does nothing after the spawn but exit with its code.
    report.handoff, _, _ = await reexec.run(
        reexec_argv(
            [
                *argv,
                *(a for stem in carried for a in ("--parked", stem)),
                "--deadline",
                render_ts(run.deadline),
                *(["--stop-lifecycle", consumer.inbox.lifecycle_id] if consumer.projection.stop_requested else []),
            ]
        ),
        cwd=checkout.repo,
        env=checkout.env,
        timeout=None,
    )
    return report


class _Drain:
    def _signal_kill(self) -> None:
        control.publish_request(self.c.config.state_dir, ControlRequest(uuid4().hex, self.c.control.inbox.lifecycle_id, "kill", None), self.c.fs)

    def __init__(self, checkout: Checkout, dispatch: Dispatch, carried: frozenset[str], *, before_dispatch: Callable[[], Awaitable[None]] | None = None, deadline: datetime | None = None) -> None:
        self.c = checkout
        self.dispatch = dispatch
        self.before_dispatch = before_dispatch
        self.carried = carried  # parked earlier in this invocation, by a parent that handed off
        self.upgrade: tuple[str, str] | None = None  # (stem, commit) of a self-upgrading admission
        self.deadline = deadline if deadline is not None else checkout.clock() + timedelta(hours=checkout.config.drain.max_runtime_hours)
        self.over_budget: dict[str, Parked] = {}  # parked at dispatch by the per-ticket ceiling
        self.storm_waiting = False
        self.provider_deadlines = []
        self.report = Report()
        self.retro = None
        self.served_retro_id: str | None = None
        self.last_dispatched: str | None = None

    async def run(self) -> Report:
        while True:
            if hasattr(self.dispatch, "prepare"):
                from dataclasses import replace

                from chupa.config import snapshot_config

                self.c = replace(self.c, config=snapshot_config(self.c.control.load_config()))
            if self.before_dispatch is not None:
                await self.before_dispatch()
            if self._stopping() or self.c.control.projection.stop_requested:
                return self.report
            await intake(self.c.repo, self.c.git, self.c.journal, self.c.fs)
            # Keep a ticket's retry cycle together before checking retro triggers.
            if self.retro is not None and await self._between_tickets():
                if hasattr(self.dispatch, "prepare"):
                    await self.dispatch.prepare()
                request_id = self.c.control.projection.retro_id
                if request_id is not None and request_id != self.served_retro_id:
                    await self._run_retro(forced=True)
                    self.served_retro_id = request_id
                else:
                    await self._run_retro(forced=False)
            material = self._offer_material()
            scan = await self._scan()
            shas = {s: await self._sha(s) for s in scan.tickets}
            prepared_events = self.c.journal.read()
            # A control wait may outlive this preparation. Compare ticket bytes again
            # before using its SHAs; changed content must return through the git seam.
            if self.before_dispatch is not None:
                await self.before_dispatch()
            if self._stopping() or self.c.control.projection.stop_requested:
                return self.report
            events = self.c.journal.read()
            if material != self._offer_material() or events != prepared_events:
                continue
            last = last_states(events)
            held = {s for s in scan.tickets if (blob := parked_blob(events, s)) is not None and blob == shas[s]}
            pick, reoffer = self._select(scan, events, last, held)
            if pick is None:
                if self.retro is not None and self.c.control.projection.retro_id is not None and self.c.control.projection.retro_id != self.served_retro_id and await self._between_tickets():
                    continue
                if self.provider_deadlines:
                    now = self.c.clock()
                    if now >= self.deadline:
                        return self._halt(scan, events, last, held)
                    deadline = min(min(self.provider_deadlines), self.deadline)
                    # Re-enter the control checkpoint while routing is unavailable.
                    await self.c.control.sleep(min(0.1, max(0, (deadline - now).total_seconds())))
                    continue
                if self.storm_waiting:
                    if self.c.clock() >= self.deadline:
                        return self._halt(scan, events, last, held)
                    await self.c.control.sleep(0.1)
                    continue
                self._settle(scan, events, last, held)
                return self.report
            if self.c.clock() >= self.deadline:
                return self._halt(scan, events, last, held)
            await self._run_one(pick, reoffer, shas[pick.stem])
            if self._stopping() or self.upgrade is not None:
                return self.report

    def _stopping(self) -> bool:
        consumer = self.c.control
        return consumer is not None and consumer.projection.lifecycle_id == consumer.inbox.lifecycle_id and consumer.projection.kill_requested

    async def _between_tickets(self) -> bool:
        stem = self.last_dispatched
        if stem is None:
            return True
        events = self.c.journal.read()
        body = next((e.body for e in reversed(events) if e.type == EventType.STATE_TRANSITION and e.ticket == stem), {})
        if body.get("to") in SETTLED | RETIRED or stem in reject_queue(events) or "provider_drought" in body:
            return True
        if self.c.control is not None and stem in self.c.control.storm_holds().values():
            return True
        if (blob := parked_blob(events, stem)) is not None and (self.c.repo / ticket_path(stem)).exists():
            sha = await self._sha(stem)
            return blob == sha
        return False

    def _offer_material(self) -> dict[str, bytes]:
        repo = self.c.repo
        paths = list((repo / TICKETS_DIR).glob(f"*/{TICKET_FILE}"))
        return {p.relative_to(repo).as_posix(): p.read_bytes() for p in paths}

    async def _scan(self) -> _Scan:
        """Committed tickets only: a ticket file dirty in the working tree is not yet on the ticket plane."""
        repo = self.c.repo
        dirty = {p for _, p in _porcelain(await self.c.git.status_porcelain(repo))}
        tickets: dict[str, Ticket] = {}
        invalid: dict[str, str] = {}
        drafts: list[str] = []
        states = last_states(self.c.journal.read())
        for path in sorted((repo / TICKETS_DIR).glob(f"*/{TICKET_FILE}")):
            stem = path.parent.name
            if states.get(stem) in SETTLED | {"rejected"}:
                continue
            rel = ticket_path(stem)
            if any(p == rel or (p.endswith("/") and rel.startswith(p)) for p in dirty):
                continue
            try:
                ticket = parse_ticket(stem, path.read_text(), repo)
            except TicketInvalid as e:
                invalid[stem] = "; ".join(f"[{f.code}] {f.message} ({f.paved_road})" for f in e.findings)
                continue
            if ticket.frontmatter.state == "draft":
                drafts.append(stem)
            tickets[stem] = ticket
        return _Scan(tickets, invalid, tuple(drafts))

    async def _sha(self, stem: str) -> str:
        """The committed `ticket.md` blob: the content identity a premise park and a retry draw are keyed to."""
        return await self.c.git.rev_parse(self.c.repo, f"HEAD:{ticket_path(stem)}")

    def _select(
        self,
        scan: _Scan,
        events: list[Event],
        last: Mapping[str, str],
        held: set[str],
    ) -> tuple[Ticket | None, bool]:
        """The next eligible dispatch in soft-edge and sort-key order, fresh or re-offered."""
        if self.c.control.projection.stop_requested:
            return None, False
        open_ = {s: t for s, t in scan.tickets.items() if t.frontmatter.state == "confirmed" and last.get(s) not in SETTLED | RETIRED}
        edges = {s: list(t.depends) for s, t in open_.items()}
        for stem in sorted(open_):
            if cycle := depends_cycle(stem, edges):
                raise Refusal(
                    f"`## Depends on` cycle among committed tickets: {' -> '.join(cycle)}", "edit one ticket on the cycle to drop the edge that inverts the intended order, then `drain` again"
                )
        from chupa.rework import settled_dependencies, supersedes_maps

        settled = settled_dependencies(events)
        maps = supersedes_maps(events)
        authored = authored_at(events)
        ready = sorted((t for t in open_.values() if t.stem not in maps and set(t.depends) <= settled), key=lambda t: sort_key(t, authored))
        candidates = []
        storm_held = set(self.c.control.storm_holds().values()) if self.c.control is not None else set()
        self.storm_waiting = False
        self.provider_deadlines = []
        for t in ready:
            if awaiting_operator(events, t.stem, self.c.config.caps):
                continue
            budget = caps.spent(self.c.config.caps, events, t.stem) is None
            if t.stem in storm_held:
                if t.stem not in self.over_budget and t.stuck_minutes <= self.c.config.drain.max_ticket_minutes and (last.get(t.stem) is None or (t.stem not in held and budget)):
                    self.storm_waiting = True
                continue
            if t.stem in self.over_budget:
                continue
            if t.stuck_minutes > self.c.config.drain.max_ticket_minutes:
                self.over_budget[t.stem] = Parked(
                    t.stem,
                    f"`## Time budget` stuck {t.stuck_minutes}m exceeds drain.max_ticket_minutes ({self.c.config.drain.max_ticket_minutes}m); never dispatched",
                    f"lower `- stuck:` in {ticket_path(t.stem)} to at most {self.c.config.drain.max_ticket_minutes}m (split the ticket if it cannot fit)",
                )
                continue
            session = self.c.control.providers
            if session.active and budget and t.stem not in held:
                tier, _ = caps.capability(t, events)
                latest = next((e.body for e in reversed(events) if e.type == EventType.STATE_TRANSITION and e.ticket == t.stem), {})
                route = latest.get("provider_drought", {"tier": tier, "surface": "implement"})
                drought = session.drought(self.c.config, route["tier"], route["surface"])
                if drought:
                    session.park(t.stem, drought)
                    if drought.deadline is not None:
                        self.provider_deadlines.append(drought.deadline)
                    continue
            if last.get(t.stem) is None:
                candidates.append((t, False))
            elif t.stem not in held and reofferable(events, t.stem, self.c.config.caps):
                candidates.append((t, True))
        if candidates:
            ordered = order_tickets((t for t, _ in candidates), authored)
            write_queue(self.c.config.state_dir, self.c.fs, self.c.clock, ordered)
            return next(pair for pair in candidates if pair[0] == ordered[0])
        return None, False

    async def _run_one(self, ticket: Ticket, reoffer: bool, sha: str) -> None:
        if self._stopping():
            return
        stem = ticket.stem
        if hasattr(self.dispatch, "prepare"):
            await self.dispatch.prepare()
        if reoffer:
            record_reoffer(self.c.journal, self.c.journal.read(), stem, sha)
        # The `ticket.md` the run answers: a `premise_failed` verdict parks the stem until this changes.
        self.c.journal.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": sha}, ticket=stem)
        self.last_dispatched = stem

        async def abort():
            await self.dispatch.abort_current()

        terminal = await self._await_controlled(asyncio.create_task(self.dispatch(ticket)), abort, self.c.control.sleep if self.c.control is not None else self.c.sleep)
        if self._stopping():
            return
        if terminal not in TERMINAL_STATES:
            raise ValueError(f"stage seam returned {terminal!r}, not a terminal state {sorted(TERMINAL_STATES)}")
        body = next(e.body for e in reversed(self.c.journal.read()) if e.type == EventType.STATE_TRANSITION and e.ticket == stem)
        if body["to"] != terminal:
            raise ValueError(f"stage seam returned {terminal!r} for {stem} but journaled {body['to']!r}; the seam must journal the run's single terminal transition")
        if terminal == "merged":
            self.report.merged.append(stem)
            # A `merged` with no commit is the no-diff settlement: nothing was admitted.
            if (commit := body.get("commit")) is not None:
                changed = await self.c.git.diff_names(self.c.repo, f"{commit}^", commit)
                if self.c.repo.resolve() == ENGINE and any(p.startswith(UPGRADE_PREFIXES) for p in changed):
                    self.upgrade = (stem, commit)

    async def _run_retro(self, *, forced):
        await self._await_controlled(asyncio.create_task(self.retro(forced=forced)), self.retro.abort_current, self.c.sleep)

    async def _await_controlled(self, task, abort, sleep):
        from chupa.daemon import _protected_cleanup

        consumer = self.c.control

        async def control() -> None:
            while not task.done():
                await sleep(0.1)
                consumer.inbox.consume()
                if self._stopping():
                    await consumer.apply_kill(abort, task)
                    return

        monitor = asyncio.create_task(control()) if consumer is not None else None
        owned = (task, monitor) if monitor is not None else (task,)
        try:
            await asyncio.wait(owned, return_when=asyncio.FIRST_COMPLETED)
            if monitor is not None and self._stopping():
                await asyncio.shield(monitor)
                self.report.killed = True
                return
            if monitor is not None and monitor.done():
                monitor.result()
            return task.result()
        finally:

            async def cleanup() -> None:
                failed_stop = False
                try:
                    if self._stopping():
                        try:
                            await consumer.apply_kill(abort, task)
                        except BaseException:
                            failed_stop = True
                            raise
                finally:
                    failed_control = failed_stop or (monitor is not None and monitor.done() and not monitor.cancelled() and monitor.exception() is not None)
                    for pending in owned:
                        # Neither a failed decision nor a failed abort authorizes
                        # dispatch cancellation. Observe its ordinary cleanup instead.
                        if pending is task and failed_control:
                            continue
                        if not pending.done() and not pending.cancelling():
                            pending.cancel()
                    results = await asyncio.gather(*owned, return_exceptions=True)
                    for result in results:
                        if isinstance(result, BaseException) and not isinstance(result, asyncio.CancelledError):
                            raise result

            await _protected_cleanup(asyncio.create_task(cleanup()))

    def parked_stems(self) -> tuple[str, ...]:
        """The invocation's parked set, carried across the handoff chain: every unsettled red plus the carried."""
        last = last_states(self.c.journal.read())
        red = {s for s, to in last.items() if to in TERMINAL_STATES - SETTLED - RETIRED}
        carried = {s for s in self.carried if last.get(s) not in SETTLED | RETIRED}
        return tuple(sorted(red | carried | set(self.over_budget)))

    def _settle(self, scan: _Scan, events: list[Event], last: Mapping[str, str], held: set[str]) -> None:
        from chupa.rework import settled_dependencies

        settled = settled_dependencies(events)
        awaiting = reject_queue(events)
        for stem in sorted(scan.tickets):
            if last.get(stem) not in SETTLED | RETIRED | {None, "running"} and caps.spent(self.c.config.caps, events, stem) is not None and stem not in awaiting:
                body = next(e.body for e in reversed(events) if e.type == EventType.STATE_TRANSITION and e.ticket == stem)
                if body.get("to") == PREMISE and "render_over_bound" in body.get("reason", "").split(","):
                    continue
                if "provider_drought" in body:
                    continue
                if body.get("routed") != "reject_queue":
                    self.c.journal.append(EventType.SIGNAL, {"signal": "reject_arrival"}, ticket=stem)
                    awaiting[stem] = body
        for stem, t in sorted(scan.tickets.items()):
            if t.frontmatter.state != "confirmed" or last.get(stem) in SETTLED | RETIRED:
                continue
            if stem in self.over_budget:
                self.report.parked.append(self.over_budget[stem])
            elif unmet := tuple(d for d in t.depends if d not in settled):
                self.report.blocked.append((stem, unmet))
            elif (to := last.get(stem)) is None:
                self.report.unadmitted.append(stem)
            else:
                body = next(e.body for e in reversed(events) if e.type == EventType.STATE_TRANSITION and e.ticket == stem)
                where = f" at {body['stage']}" if "stage" in body else ""
                spent_cap = caps.spent(self.c.config.caps, events, stem)
                drawn = caps.failed_attempts(events, stem) if spent_cap == "attempts" else caps.draws(events, stem, spent_cap or "retry")
                cap_limit = getattr(self.c.config.caps, spent_cap or "retry")
                if stem in held and spent_cap is None and to == "gate_failed":
                    why = f"{to}{where}; parked until its committed ticket.md changes"
                    road = f"split or shrink the ticket under the diff budget and commit the `ticket.md` change, or retire it with `./dev.py reject {stem}`"
                elif stem in held and spent_cap is None:
                    why, road = f"{to}{where}; parked until its committed ticket.md changes", self._premise_road(t)
                elif spent_cap is None:  # only a halt leaves budget unspent: the continuing drain re-offers it
                    why, road = (f"{to}{where}; {cap_limit - drawn} of {cap_limit} retry units left", "`uv run python -m chupa drain` re-offers it")
                else:
                    why, road = (
                        f"{to}{where}; {caps.spent_reason(spent_cap)} ({drawn}/{cap_limit})",
                        "read the findings below and the engine log; fix the ticket and author a successor stem -- a `ticket.md` edit never re-arms the cap",
                    )
                if stem in awaiting:
                    if "ticket_changed" in awaiting[stem].get("reason", "").split(","):
                        why = f"{to}{where}; ticket_changed; held for an operator"
                        road = f"review the change to {ticket_path(stem)}, then keep (./dev.py confirm {stem}) or kill (./dev.py reject {stem})"
                    elif not (stem in held and to == "gate_failed" and spent_cap is None):
                        road = f"edit {ticket_path(stem)}, then uv run python -m chupa confirm {stem}; or retire it with uv run python -m chupa reject {stem}"
                findings = self._findings(stem)
                if to == PREMISE and body.get("stage") == "requisition":
                    findings = (body["reason"], *findings)
                self.report.parked.append(Parked(stem, why, road, findings))
        self.report.invalid = sorted(scan.invalid.items())
        self.report.drafts = list(scan.drafts)

    def _premise_road(self, t: Ticket) -> str:
        """Name the ticket edit that releases a premise park."""
        body = next(e.body for e in reversed(self.c.journal.read()) if e.type == EventType.STATE_TRANSITION and e.ticket == t.stem)
        if "render_over_bound" in body.get("reason", "").split(","):
            return "shrink or split the committed ticket text and rerun drain"
        rel = ticket_path(t.stem)
        return f"answer the premise findings below by editing {rel} and committing it -- the content change releases it"

    def _findings(self, stem: str) -> tuple[str, ...]:
        """Where the parked stem's detail lives: its durable ticket-plane artifacts."""
        root = self.c.repo / TICKETS_DIR / stem
        return tuple(p.relative_to(self.c.repo).as_posix() for p in sorted(root.rglob("*")) if p.is_file() and p.name != TICKET_FILE)

    def _halt(self, scan: _Scan, events: list[Event], last: Mapping[str, str], held: set[str]) -> Report:
        hours = self.c.config.drain.max_runtime_hours
        self.c.journal.append(EventType.SIGNAL, {"signal": HALT_SIGNAL, "ceiling": CEILING, "hours": hours, "merged": list(self.report.merged)})
        self._settle(scan, events, last, held)
        self.report.halted = f"{hours}h elapsed"
        return self.report
