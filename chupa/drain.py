"""The `drain` scaffold verb (CHUPA_PLAN.md sections 9, 11.2, 18, 19.P1): run the ready queue to quiescence.

One ticket at a time, in the one process holding the single-writer lock, through the same dispatch seam as
`run <stem>`. A non-ok terminal parks its stem and the drain moves on; at quiescence each parked stem with
`retry` budget left is re-offered, one journaled `cap_consumed` unit per re-offer, findings-fed: the Implement
render folds the prior terminal's durable findings into criteria-position (section 11.2). Every selection re-scans
the committed tickets dir and re-folds the journal, so a merge or a ticket-plane commit landed mid-invocation
is visible to the very next pick. This is the eligibility sort's owner (section 9).

An admission touching `chupa/**` or `specs/**` is a SELF-UPGRADE: before the next dispatch the drain hands off to
a re-exec'd child running the upgraded checkout (section 18's HANDOFF), carrying the invocation's parked set in
argv. A `premise_failed` stem stays parked, across invocations, until its committed `ticket.md` content changes.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import timedelta

from chupa import caps
from chupa.journal import TERMINAL_STATES, Event, EventType
from chupa.lockfile import Lockfile
from chupa.reconcile import reconcile
from chupa.runner import EXIT_MERGED, EXIT_TICKET, Checkout, Dispatch, Refusal, harvest_orphan
from chupa.seams import ProcessExec
from chupa.status import last_states, reject_queue
from chupa.tickets import (
    INTAKE_SIGNAL, PLAN_FILE, TICKET_FILE, TICKETS_DIR, Ticket, TicketInvalid, _porcelain, depends_cycle, intake,
    parse_ticket, ticket_path,
)

HALT_SIGNAL = "drain_halted"
CEILING = "drain.max_runtime_hours"
# `already_satisfied` settles the stem as a no-op (section 7): it satisfies `depends` and is never re-offered.
SETTLED = frozenset({"merged", "already_satisfied"})
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
    for e in events:
        if e.type == EventType.STATE_TRANSITION and e.ticket == stem:
            last = e.body.get("to")
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

    @property
    def exit_code(self) -> int:
        if self.handoff is not None:
            return self.handoff
        # Section 18: quiescence is 0 whatever it parked; a ceiling halt is a non-quiescent stop.
        return EXIT_TICKET if self.halted else EXIT_MERGED

    def render(self) -> str:
        def block(name: str, lines: Iterable[str]) -> str:
            return f"{name}:\n" + ("\n".join(f"- {line}" for line in lines) or "(none)")

        if self.halted:
            head = (f"drain HALTED by the {CEILING} ceiling ({self.halted}) -- NOT quiescent; no new ticket was"
                    " admitted. Continue with `uv run python -m chupa drain`.")
        elif not (self.merged or self.parked or self.blocked):
            head = "drain quiescent: nothing eligible (empty ready set)."
        else:
            head = "drain quiescent: nothing eligible, unparked, re-offerable, or newly authored."
        parked = (f"{p.stem}: {p.reason} -- {p.paved_road}"
                  + "".join(f"\n  - {f}" for f in p.findings) for p in self.parked)
        return "\n\n".join((
            head,
            block("merged this invocation", self.merged),
            block("parked", parked),
            block("eligible, not admitted", self.unadmitted),
            block("blocked on unmerged depends", (f"{s}: waits on {', '.join(d)}" for s, d in self.blocked)),
            block("invalid committed tickets", (f"{s}: {why}" for s, why in self.invalid)),
            block("drafts awaiting confirm", self.drafts),
        )) + "\n"


@dataclass(frozen=True)
class _Scan:
    tickets: dict[str, Ticket]
    invalid: dict[str, str]
    drafts: tuple[str, ...]


async def drain(
    checkout: Checkout, dispatch: Dispatch, *, reexec: ProcessExec, parked: Iterable[str] = (),
) -> Report:
    """`reexec` is the handoff's own process seam (section 15): never the instance active work spawns through."""
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo),
                    clock=checkout.clock)
    lock.acquire()
    try:
        assert checkout.config.worktree_root is not None  # resolved at config load
        await reconcile(checkout.journal, checkout.git, checkout.repo, checkout.config.worktree_root,
                        lambda stem, attempt: harvest_orphan(checkout, stem, attempt))
        await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs)
        run = _Drain(checkout, dispatch, frozenset(parked))
        report = await run.run()
        if run.upgrade is None:
            return report
        stem, commit = run.upgrade
        carried = run.parked_stems()
        checkout.journal.append(EventType.SIGNAL, {"signal": HANDOFF_SIGNAL, "commit": commit,
                                                   "parked": list(carried), "merged": list(report.merged)},
                                ticket=stem)
        checkout.journal.close()
    finally:
        lock.release()
    # The fixed HANDOFF order (section 18): journaled, journal closed, lock free -- the child is the only writer,
    # and the parent does nothing after the spawn but exit with its code.
    report.handoff, _, _ = await reexec.run(reexec_argv(carried), cwd=checkout.repo, env=checkout.env, timeout=None)
    return report


class _Drain:
    def __init__(self, checkout: Checkout, dispatch: Dispatch, carried: frozenset[str]) -> None:
        self.c = checkout
        self.dispatch = dispatch
        self.carried = carried  # parked earlier in this invocation, by a parent that handed off
        self.upgrade: tuple[str, str] | None = None  # (stem, commit) of a self-upgrading admission
        self.deadline = checkout.clock() + timedelta(hours=checkout.config.drain.max_runtime_hours)
        self.over_budget: dict[str, Parked] = {}  # parked at dispatch by the per-ticket ceiling
        self.report = Report()

    async def run(self) -> Report:
        while True:
            scan = await self._scan()
            events = self.c.journal.read()
            last = last_states(events)
            held = {s for s in scan.tickets
                    if last.get(s) == PREMISE and premise_parked(events, s, await self._sha(s))}
            pick, reoffer = self._select(scan, events, last, held)
            if pick is None:
                self._settle(scan, events, last, held)
                return self.report
            if self.c.clock() >= self.deadline:
                return self._halt(scan, events, last, held)
            await self._run_one(pick, reoffer, await self._sha(pick.stem))
            if self.upgrade is not None:
                return self.report

    async def _scan(self) -> _Scan:
        """Committed tickets only: a ticket file dirty in the working tree is not yet on the ticket plane."""
        repo = self.c.repo
        dirty = {p for _, p in _porcelain(await self.c.git.status_porcelain(repo))}
        plan_file = repo / PLAN_FILE
        plan = plan_file.read_text() if plan_file.is_file() else None
        tickets: dict[str, Ticket] = {}
        invalid: dict[str, str] = {}
        drafts: list[str] = []
        for path in sorted((repo / TICKETS_DIR).glob(f"*/{TICKET_FILE}")):
            stem = path.parent.name
            rel = ticket_path(stem)
            if any(p == rel or (p.endswith("/") and rel.startswith(p)) for p in dirty):
                continue
            try:
                ticket = parse_ticket(stem, path.read_text(), repo, plan=plan)
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
        self, scan: _Scan, events: list[Event], last: Mapping[str, str], held: set[str],
    ) -> tuple[Ticket | None, bool]:
        """The next dispatch: fresh eligible work first, then re-offers, each in (priority, age) order."""
        open_ = {s: t for s, t in scan.tickets.items()
                 if t.frontmatter.state == "confirmed" and last.get(s) not in SETTLED | RETIRED}
        edges = {s: list(t.depends) for s, t in open_.items()}
        for stem in sorted(open_):
            if cycle := depends_cycle(stem, edges):
                raise Refusal(f"`## Depends on` cycle among committed tickets: {' -> '.join(cycle)}",
                              f"edit one ticket on the cycle to drop the edge that inverts the intended order,"
                              f" then `drain` again")
        authored = authored_at(events)
        ready = sorted((t for t in open_.values() if all(last.get(d) in SETTLED for d in t.depends)),
                       key=lambda t: sort_key(t, authored))
        awaiting = reject_queue(events)
        fresh, reoffers = [], []
        for t in ready:
            if t.stem in awaiting:
                continue
            if t.stem in self.over_budget:
                continue
            if t.stuck_minutes > self.c.config.drain.max_ticket_minutes:
                self.over_budget[t.stem] = Parked(
                    t.stem, f"`## Time budget` stuck {t.stuck_minutes}m exceeds drain.max_ticket_minutes"
                    f" ({self.c.config.drain.max_ticket_minutes}m); never dispatched",
                    f"lower `- stuck:` in {ticket_path(t.stem)} to at most"
                    f" {self.c.config.drain.max_ticket_minutes}m (split the ticket if it cannot fit)")
                continue
            if last.get(t.stem) is None:
                fresh.append(t)
            elif t.stem not in held and caps.spent(self.c.config.caps, events, t.stem) is None:
                reoffers.append(t)
        if fresh:
            return fresh[0], False
        if reoffers:
            return reoffers[0], True
        return None, False

    async def _run_one(self, ticket: Ticket, reoffer: bool, sha: str) -> None:
        stem = ticket.stem
        if reoffer and last_states(self.c.journal.read()).get(stem) != PREMISE:
            # The draw precedes the dispatch: a crash mid-run never hands the stem a free attempt.
            caps.consume(self.c.journal, stem, "retry", sha)
        # The `ticket.md` the run answers: a `premise_failed` verdict parks the stem until this changes.
        self.c.journal.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": sha}, ticket=stem)
        terminal = await self.dispatch(ticket)
        if terminal not in TERMINAL_STATES:
            raise ValueError(f"stage seam returned {terminal!r}, not a terminal state {sorted(TERMINAL_STATES)}")
        body = next(e.body for e in reversed(self.c.journal.read())
                    if e.type == EventType.STATE_TRANSITION and e.ticket == stem)
        if body["to"] != terminal:
            raise ValueError(f"stage seam returned {terminal!r} for {stem} but journaled {body['to']!r};"
                             " the seam must journal the run's single terminal transition")
        if terminal == "merged":
            self.report.merged.append(stem)
            # A `merged` with no commit is the no-diff settlement (section 7): nothing was admitted.
            if (commit := body.get("commit")) is not None:
                changed = await self.c.git.diff_names(self.c.repo, f"{commit}^", commit)
                if any(p.startswith(UPGRADE_PREFIXES) for p in changed):
                    self.upgrade = (stem, commit)

    def parked_stems(self) -> tuple[str, ...]:
        """The invocation's parked set, carried across the handoff chain: every unsettled red plus the carried."""
        last = last_states(self.c.journal.read())
        red = {s for s, to in last.items() if to in TERMINAL_STATES - SETTLED - RETIRED}
        carried = {s for s in self.carried if last.get(s) not in SETTLED | RETIRED}
        return tuple(sorted(red | carried | set(self.over_budget)))

    def _settle(self, scan: _Scan, events: list[Event], last: Mapping[str, str], held: set[str]) -> None:
        awaiting = reject_queue(events)
        for stem in sorted(scan.tickets):
            if (last.get(stem) not in SETTLED | RETIRED | {None, "running"}
                    and caps.spent(self.c.config.caps, events, stem) is not None
                    and stem not in awaiting):
                body = next(e.body for e in reversed(events)
                            if e.type == EventType.STATE_TRANSITION and e.ticket == stem)
                if body.get("routed") != "reject_queue":
                    self.c.journal.append(EventType.SIGNAL, {"signal": "reject_arrival"}, ticket=stem)
                    awaiting[stem] = body
        for stem, t in sorted(scan.tickets.items()):
            if t.frontmatter.state != "confirmed" or last.get(stem) in SETTLED | RETIRED:
                continue
            if stem in self.over_budget:
                self.report.parked.append(self.over_budget[stem])
            elif unmet := tuple(d for d in t.depends if last.get(d) not in SETTLED):
                self.report.blocked.append((stem, unmet))
            elif (to := last.get(stem)) is None:
                self.report.unadmitted.append(stem)
            else:
                body = next(e.body for e in reversed(events)
                            if e.type == EventType.STATE_TRANSITION and e.ticket == stem)
                where = f" at {body['stage']}" if "stage" in body else ""
                spent_cap = caps.spent(self.c.config.caps, events, stem)
                drawn = caps.draws(events, stem, spent_cap or "retry")
                cap_limit = getattr(self.c.config.caps, spent_cap or "retry")
                if stem in held:
                    why, road = f"{to}{where}; parked until its committed ticket.md changes", self._premise_road(t)
                elif spent_cap is None:  # only a halt leaves budget unspent: the continuing drain re-offers it
                    why, road = (f"{to}{where}; {cap_limit - drawn} of {cap_limit} retry units left",
                                 "`uv run python -m chupa drain` re-offers it")
                else:
                    why, road = (f"{to}{where}; {caps.spent_reason(spent_cap)} ({drawn}/{cap_limit})",
                                 "read the findings below and the engine log; fix the cause in the plan (or the"
                                 " ticket if provably not the plan's) and author a successor stem -- a"
                                 " `ticket.md` edit never re-arms the cap")
                if stem in awaiting:
                    road = (f"edit {ticket_path(stem)} (or fix the plan and regenerate it), then "
                            f"uv run python -m chupa confirm {stem}; or retire it with "
                            f"uv run python -m chupa reject {stem}")
                self.report.parked.append(Parked(stem, why, road, self._findings(stem)))
        self.report.invalid = sorted(scan.invalid.items())
        self.report.drafts = list(scan.drafts)

    def _premise_road(self, t: Ticket) -> str:
        """`source`-keyed (section 18): the release is the same commit, only where the fix originates differs."""
        rel = ticket_path(t.stem)
        if t.frontmatter.source == "seed":
            return (f"the verdict below names a false assumption in CHUPA_PLAN.md: fix it in the plan and commit that"
                    f" first, then commit the plan-congruent correction of {rel} -- that ticket.md change releases it")
        return f"answer the premise findings below by editing {rel} and committing it -- the content change releases it"

    def _findings(self, stem: str) -> tuple[str, ...]:
        """Where the parked stem's detail lives: its durable ticket-plane artifacts (section 10)."""
        root = self.c.repo / TICKETS_DIR / stem
        return tuple(p.relative_to(self.c.repo).as_posix() for p in sorted(root.rglob("*"))
                     if p.is_file() and p.name != TICKET_FILE)

    def _halt(self, scan: _Scan, events: list[Event], last: Mapping[str, str], held: set[str]) -> Report:
        hours = self.c.config.drain.max_runtime_hours
        self.c.journal.append(EventType.SIGNAL, {"signal": HALT_SIGNAL, "ceiling": CEILING, "hours": hours,
                                                 "merged": list(self.report.merged)})
        self._settle(scan, events, last, held)
        self.report.halted = f"{hours}h elapsed"
        return self.report
