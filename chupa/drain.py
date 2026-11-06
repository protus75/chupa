"""The `drain` scaffold verb (CHUPA_PLAN.md sections 9, 11.2, 18, 19.P1): run the ready queue to quiescence.

One ticket at a time, in the one process holding the single-writer lock, through the same dispatch seam as
`run <stem>`. A non-ok terminal parks its stem and the drain moves on; at quiescence each parked stem with
`retry` budget left is re-offered, one journaled `cap_consumed` unit per re-offer, findings-fed: the Implement
render folds the prior terminal's durable findings into criteria-position (section 11.2). Every selection re-scans
the committed tickets dir and re-folds the journal, so a merge or a ticket-plane commit landed mid-invocation
is visible to the very next pick. This is the eligibility sort's owner (section 9).

An admission touching `chupa/**` or `specs/**` is a SELF-UPGRADE: before the next dispatch the drain hands off to
a re-exec'd child running the upgraded checkout (section 18's HANDOFF), carrying the invocation's parked set in
argv. A `premise_failed` stem stays parked until its committed `ticket.md` changes.
"""

import asyncio
import json
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import timedelta

from chupa import caps
from chupa.journal import TERMINAL_STATES, Event, EventType, render_ts
from chupa.lockfile import Lockfile
from chupa.reconcile import reconcile
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
    read_plan,
    ticket_path,
)

HALT_SIGNAL = "drain_halted"
CEILING = "drain.max_runtime_hours"
# A `rejected` stem is retired (section 11.2): never dispatched again.
RETIRED = frozenset({"rejected"})
PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

PREMISE = "premise_failed"
HANDOFF_SIGNAL = "drain_handoff"
# The engine plane the running process has loaded: admitting a change under either re-execs the drain.
UPGRADE_PREFIXES = ("chupa/", "specs/")
# D1's one named runtime `uv` exception (section 18): one form, dependency changes included.
REEXEC = ("uv", "run", "python", "-m", "chupa", "drain")


def reexec_argv(parked: Iterable[str]) -> list[str]:
    return [*REEXEC, *(a for stem in parked for a in ("--parked", stem))]


def premise_parked(events: Iterable[Event], stem: str, ticket_sha: str) -> bool:
    """The premise park (section 18): the stem's last run ended `premise_failed` against this same `ticket.md`."""
    last: str | None = None
    ran_sha: str | None = None
    body: Mapping = {}
    for e in events:
        if e.type == EventType.STATE_TRANSITION and e.ticket == stem:
            body = e.body
            last = body.get("to")
            if last == "running":
                ran_sha = e.body.get("ticket_sha")
    return last == PREMISE and ran_sha == ticket_sha


def authored_at(events: Iterable[Event]) -> dict[str, str]:
    """Each stem's age anchor (section 9): the `ts` of its FIRST ticket-plane authoring-commit event."""
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

    @property
    def exit_code(self) -> int:
        if self.handoff is not None:
            return self.handoff
        # Section 18: quiescence is 0 whatever it parked; a ceiling halt is a non-quiescent stop.
        return EXIT_TICKET if self.halted or self.killed else EXIT_MERGED

    def render(self) -> str:
        def block(name: str, lines: Iterable[str]) -> str:
            return f"{name}:\n" + ("\n".join(f"- {line}" for line in lines) or "(none)")

        if self.killed:
            head = "drain stopped by kill -- NOT quiescent. Continue with `uv run python -m chupa drain`."
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
    before_dispatch: Callable[[], Awaitable[None]] | None = None,
) -> Report:
    """`reexec` is the handoff's own process seam (section 15): never the instance active work spawns through."""
    consumer = checkout.control
    if consumer is None:
        raise Refusal("admission control consumer absent", "construct it with `build_control` at the composition root and supply it as `Checkout.control`")
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    lock.acquire()
    try:
        consumer.publish()

        async def checkpoint() -> None:
            await consumer.checkpoint()
            if consumer.projection.lifecycle_id == consumer.inbox.lifecycle_id and consumer.projection.kill_requested:
                return
            if before_dispatch is not None:
                await before_dispatch()
            # An injected preparation wait can allow a new request to arrive.
            await consumer.checkpoint()

        assert checkout.config.worktree_root is not None  # resolved at config load
        await reconcile(checkout.journal, checkout.git, checkout.repo, checkout.config.worktree_root, lambda stem, attempt: harvest_orphan(checkout, stem, attempt))
        consumer.providers.timers.reconstruct()
        consumer.providers.timers.fire_due()
        if hasattr(dispatch, "prepare"):
            await dispatch.prepare()
        await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs)
        run = _Drain(checkout, dispatch, frozenset(parked), before_dispatch=checkpoint)
        run.retro = getattr(dispatch, "_retro", None)
        report = await run.run()
        # A pending self-upgrade is still an offer boundary, never permission to
        # launch a child after a kill accepted during the final preparation.
        await consumer.checkpoint()
        if run._stopping():
            await consumer.apply_kill(dispatch.abort_current)
            report.killed = True
            return report
        if run.upgrade is None:
            return report
        stem, commit = run.upgrade
        carried = run.parked_stems()
        checkout.journal.append(EventType.SIGNAL, {"signal": HANDOFF_SIGNAL, "commit": commit, "parked": list(carried), "merged": list(report.merged)}, ticket=stem)
        checkout.journal.close()
    finally:
        try:
            try:
                await consumer.providers.close()
            finally:
                consumer.retire()
        finally:
            lock.release()
    # The fixed HANDOFF order (section 18): journaled, journal closed, lock free -- the child is the only writer,
    # and the parent does nothing after the spawn but exit with its code.
    report.handoff, _, _ = await reexec.run(reexec_argv(carried), cwd=checkout.repo, env=checkout.env, timeout=None)
    return report


class _Drain:
    def __init__(self, checkout: Checkout, dispatch: Dispatch, carried: frozenset[str], *, before_dispatch: Callable[[], Awaitable[None]] | None = None) -> None:
        self.c = checkout
        self.dispatch = dispatch
        self.before_dispatch = before_dispatch
        self.carried = carried  # parked earlier in this invocation, by a parent that handed off
        self.upgrade: tuple[str, str] | None = None  # (stem, commit) of a self-upgrading admission
        self.deadline = checkout.clock() + timedelta(hours=checkout.config.drain.max_runtime_hours)
        self.over_budget: dict[str, Parked] = {}  # parked at dispatch by the per-ticket ceiling
        self.storm_waiting = False
        self.provider_deadlines = []
        self.report = Report()
        self.retro = None
        self.last_dispatched: str | None = None

    async def run(self) -> Report:
        while True:
            if hasattr(self.dispatch, "prepare"):
                from dataclasses import replace

                from chupa.config import snapshot_config

                self.c = replace(self.c, config=snapshot_config(self.c.control.load_config()))
            if self.before_dispatch is not None:
                await self.before_dispatch()
            if self._stopping():
                return self.report
            # Keep a ticket's retry cycle together before checking retro triggers.
            if self.retro is not None and await self._between_tickets():
                if hasattr(self.dispatch, "prepare"):
                    await self.dispatch.prepare()
                await self._run_retro(forced=False)
            material = self._offer_material()
            scan = await self._scan()
            shas = {s: await self._sha(s) for s in scan.tickets}
            prepared_events = self.c.journal.read()
            # A control wait may outlive this preparation. Compare ticket bytes again
            # before using its SHAs; changed content must return through the git seam.
            if self.before_dispatch is not None:
                await self.before_dispatch()
            if self._stopping():
                return self.report
            events = self.c.journal.read()
            if material != self._offer_material() or events != prepared_events:
                continue
            last = last_states(events)
            held = {s for s in scan.tickets if last.get(s) == PREMISE and premise_parked(events, s, shas[s])}
            pick, reoffer = self._select(scan, events, last, held)
            if pick is None:
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
        if body.get("to") == PREMISE and (self.c.repo / ticket_path(stem)).exists():
            return premise_parked(events, stem, await self._sha(stem))
        return False

    def _offer_material(self) -> dict[str, bytes]:
        repo = self.c.repo
        paths = list((repo / TICKETS_DIR).glob(f"*/{TICKET_FILE}"))
        return {p.relative_to(repo).as_posix(): p.read_bytes() for p in paths}

    async def _scan(self) -> _Scan:
        """Committed tickets only: a ticket file dirty in the working tree is not yet on the ticket plane."""
        repo = self.c.repo
        dirty = {p for _, p in _porcelain(await self.c.git.status_porcelain(repo))}
        plan = read_plan(repo)
        tickets: dict[str, Ticket] = {}
        invalid: dict[str, str] = {}
        drafts: list[str] = []
        states = last_states(self.c.journal.read())
        for path in sorted((repo / TICKETS_DIR).glob(f"*/{TICKET_FILE}")):
            stem = path.parent.name
            rel = ticket_path(stem)
            if any(p == rel or (p.endswith("/") and rel.startswith(p)) for p in dirty):
                continue
            try:
                ticket = parse_ticket(stem, path.read_text(), repo, plan=plan)
            except TicketInvalid as e:
                if states.get(stem) not in SETTLED | RETIRED:
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
        awaiting = reject_queue(events)
        candidates = []
        storm_held = set(self.c.control.storm_holds().values()) if self.c.control is not None else set()
        self.storm_waiting = False
        self.provider_deadlines = []
        for t in ready:
            if t.stem in awaiting and "ticket_changed" in awaiting[t.stem].get("reason", "").split(","):
                continue
            budget = caps.spent(self.c.config.caps, events, t.stem) is None
            if t.stem in storm_held:
                if t.stem not in self.over_budget and t.stuck_minutes <= self.c.config.drain.max_ticket_minutes and (last.get(t.stem) is None or (t.stem not in held and budget)):
                    self.storm_waiting = True
                continue
            if t.stem in awaiting and not budget:
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
            elif t.stem not in held and budget:
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
            history = self.c.journal.read()
            queued = reject_queue(history)
            if stem in queued:
                self.c.journal.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}, ticket=stem)
            body = next(e.body for e in reversed(history) if e.type == EventType.STATE_TRANSITION and e.ticket == stem and e.body.get("to") in TERMINAL_STATES)
            draw_retry = body.get("to") != PREMISE and "provider_drought" not in body
            if draw_retry:
                caps.consume(self.c.journal, stem, "retry", sha, rung=body.get("rung"))
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
            # A `merged` with no commit is the no-diff settlement (section 7): nothing was admitted.
            if (commit := body.get("commit")) is not None:
                changed = await self.c.git.diff_names(self.c.repo, f"{commit}^", commit)
                if any(p.startswith(UPGRADE_PREFIXES) for p in changed):
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
                if stem in held and spent_cap is None:
                    why, road = f"{to}{where}; parked until its committed ticket.md changes", self._premise_road(t)
                elif spent_cap is None:  # only a halt leaves budget unspent: the continuing drain re-offers it
                    why, road = (f"{to}{where}; {cap_limit - drawn} of {cap_limit} retry units left", "`uv run python -m chupa drain` re-offers it")
                else:
                    why, road = (
                        f"{to}{where}; {caps.spent_reason(spent_cap)} ({drawn}/{cap_limit})",
                        "read the findings below and the engine log; fix the ticket and author a successor stem -- a"
                        " `ticket.md` edit never re-arms the cap",
                    )
                if stem in awaiting:
                    if "ticket_changed" in awaiting[stem].get("reason", "").split(","):
                        why = f"{to}{where}; ticket_changed; held for an operator"
                        road = f"review the change to {ticket_path(stem)}, then keep (./dev.py confirm {stem}) or kill (./dev.py reject {stem})"
                    else:
                        road = f"edit {ticket_path(stem)}, then uv run python -m chupa confirm {stem}; or retire it with uv run python -m chupa reject {stem}"
                self.report.parked.append(Parked(stem, why, road, self._findings(stem)))
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
        """Where the parked stem's detail lives: its durable ticket-plane artifacts (section 10)."""
        root = self.c.repo / TICKETS_DIR / stem
        return tuple(p.relative_to(self.c.repo).as_posix() for p in sorted(root.rglob("*")) if p.is_file() and p.name != TICKET_FILE)

    def _halt(self, scan: _Scan, events: list[Event], last: Mapping[str, str], held: set[str]) -> Report:
        hours = self.c.config.drain.max_runtime_hours
        self.c.journal.append(EventType.SIGNAL, {"signal": HALT_SIGNAL, "ceiling": CEILING, "hours": hours, "merged": list(self.report.merged)})
        self._settle(scan, events, last, held)
        self.report.halted = f"{hours}h elapsed"
        return self.report
