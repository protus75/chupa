"""The `run <stem>` scaffold verb: one ticket through intake, the
single-writer lockfile, and the stage-dispatch seam, all in the one process holding the lock.

Exit codes: 0 merged, 1 a non-ok ticket terminal, 2 an engine-plane refusal.
"""

import asyncio
import os
import sys
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, assert_never, cast

if TYPE_CHECKING:
    from chupa.daemon import PauseConsumer

import yaml

from chupa.artifacts import Cost, Finding, Harvest, StageResult
from chupa.box import BOX_DIR
from chupa.caps import capability, consume, next_rung, spent, spent_reason
from chupa.config import Config, ConfigSnapshot, snapshot_config
from chupa.driver import Driver
from chupa.effects import Effects
from chupa.enginelog import EngineLog
from chupa.git import Git, GitError
from chupa.journal import TERMINAL_STATES, Event, EventType, Journal, dispatch_of, run_seq
from chupa.journal import Dispatch as JournalDispatch
from chupa.llm import LLM
from chupa.lockfile import Lockfile
from chupa.merge import compose_pipeline, merge
from chupa.providers import ProviderCallError, ProviderDrought, ProviderLLM
from chupa.reconcile import reconcile
from chupa.redact import Redactor
from chupa.seams import Clock, FileSystem, GroupExec, Sleep
from chupa.stages import DiagnosisMaterial, StageContext, StagesRun, diagnose, lift_outbox, run_stages, ticket_change_findings, write_diagnosis
from chupa.status import SETTLED, last_states, run_admission, verdict_refusal
from chupa.storm import arrival_id
from chupa.tickets import Ticket, TicketInvalid, intake, parse_ticket, split_frontmatter, stamp, stem_findings, ticket_path, validate_ticket

EXIT_MERGED = 0
EXIT_TICKET = 1
EXIT_REFUSED = 2

# Engine plane: the prompt specs ship with the engine, not the host checkout it runs against.
SPECS_DIR = Path(__file__).resolve().parent / "specs"
HARVEST_TAIL_CHARS = 4_000
IDENTICAL_K = 3

# The stage seam: drives the validated ticket through the stages and merge, journals the run's single
# terminal transition, and returns that terminal state.
Dispatch = Callable[[Ticket], Awaitable[str]]


# The provider backstop is the drain ceiling every ticket stuck budget fits under:
# the ticket's own stuck budget is the bound the driver enforces, never a shorter per-call cap.
def call_timeout(config: Config) -> float:
    return config.drain.max_ticket_minutes * 60.0


class Refusal(Exception):
    """An engine-plane refusal (exit 2): nothing was dispatched."""

    def __init__(self, message: str, paved_road: str) -> None:
        super().__init__(f"{message} -- {paved_road}")


@dataclass(frozen=True)
class Checkout:
    """The composed seams one invocation runs against; the stage pipeline is built from it."""

    repo: Path
    config: Config | ConfigSnapshot
    env: Mapping[str, str]
    exec_: GroupExec
    git: Git
    journal: Journal
    fs: FileSystem
    clock: Clock
    sleep: Sleep = asyncio.sleep
    control: "PauseConsumer | None" = None


Pipeline = Callable[[Checkout], Dispatch]


def pipeline(checkout: Checkout) -> Dispatch:
    """Preparation belongs to the outer lock-held run/drain lifetime."""

    class PreparedDispatch:
        callback = None
        snapshot = None
        stages = None

        async def prepare(self):
            snapshot = snapshot_config(checkout.control.load_config())
            if self.callback is not None and snapshot == self.snapshot:
                return
            local = replace(checkout, config=snapshot)
            self.callback = await prepare_pipeline(local)
            self.stages = self.callback.stages
            self.snapshot = snapshot

        async def __call__(self, ticket):
            if self.callback is None:
                await self.prepare()
            try:
                return await self.callback(ticket)
            finally:
                self.callback = None

        async def abort_current(self):
            if self.callback is not None:
                await self.callback.abort_current()

    return PreparedDispatch()


async def prepare_pipeline(checkout: Checkout) -> Dispatch:
    """Preflight this checkout's providers before constructing any stage consumers."""
    llm = ProviderLLM(checkout.config, exec_=checkout.exec_, fs=checkout.fs, env=checkout.env, cwd=checkout.repo, timeout=call_timeout(checkout.config), session=checkout.control.providers)
    log = EngineLog(checkout.config.state_dir / "engine.log", Redactor.from_config(checkout.config, checkout.env), checkout.clock)
    log.event("phase_start", phase="preflight")
    try:
        problems = await llm.preflight()
    except BaseException:
        log.event("phase_end", phase="preflight", outcome="failed")
        raise
    log.event("phase_end", phase="preflight", outcome="failed" if problems else "ok")
    for notice in llm.preflight_notices:
        print(f"chupa: provider preflight notice: {notice}", file=sys.stderr)
    if problems:
        raise Refusal("provider preflight failed: " + "; ".join(problems), "fix each named provider, then run the same command again (provider preflight)")
    return bind(checkout, llm)


def bind(checkout: Checkout, llm: LLM) -> Dispatch:
    driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
    driver.journal = checkout.journal
    driver.effects = Effects(checkout.journal)
    ctx = StageContext(repo=checkout.repo, config=checkout.config, env=checkout.env, exec_=checkout.exec_, git=checkout.git, fs=checkout.fs, driver=driver, specs_dir=SPECS_DIR)

    def escalate(event: Event) -> None:
        # Queue signals are already journaled; notification transport is handled separately.
        return None

    from chupa.daemon import TicketWriter

    queue = compose_pipeline(ctx, escalate=escalate, control=checkout.control)
    return TicketWriter(ctx, queue)


async def drive(ctx: StageContext, ticket: Ticket, *, admission=None, consume_handoff=None) -> str:
    """Implement -> Check -> Review -> Merge; harvest, dispatch, journal, then wipe a non-ok run."""
    run = None
    if ctx.boundary.run is None:
        tier, effort = capability(ticket, ctx.driver.journal.read())
        ticket = replace(ticket, frontmatter=ticket.frontmatter.model_copy(update={"agent_tier": tier, "agent_effort": effort}))
        sha = await ctx.git.rev_parse(ctx.repo, f"HEAD:{ticket_path(ticket.stem)}")
        history = ctx.driver.journal.read()
        approved = any(
            e.type == EventType.SIGNAL and e.ticket == ticket.stem and e.body.get("signal") == "requisition_verdict" and e.body.get("verdict") == "approve" and e.body.get("ticket_sha") == sha
            for e in history
        )
        if not approved:
            from chupa.driver import ProviderDroughtResult
            from chupa.requisition import prior_review, review_ticket

            attempt = run_seq(history, ticket.stem)
            text = await ctx.git._run(ctx.repo, "show", f"HEAD:{ticket_path(ticket.stem)}")
            try:
                review = await review_ticket(
                    ctx.driver,
                    repo=ctx.repo,
                    stem=ticket.stem,
                    text=text,
                    specs_dir=ctx.specs_dir,
                    coverage_map=ctx.config.state_dir / "coverage-map.json" if ctx.config.review.coverage_map is not None else None,
                    tier=tier,
                    stem_slot=ticket.stem,
                    run_seq=attempt,
                    attempt=attempt,
                    call_seq=1,
                    expected_budget=ticket.expected_minutes * 60,
                    prior=await prior_review(ctx.git, ctx.repo, history, ticket.stem, text),
                )
            except ProviderDrought as exc:
                result = ProviderDroughtResult(outcome="infra_error", artifact=None, findings=[], cost=Cost(), provider_drought=exc.record)
                run = StagesRun(attempt=attempt, results={"implement": result}, ticket_sha=sha)
            except ProviderCallError as exc:
                findings = await ctx.driver.provider_failure(exc, owner=ticket.stem, ticket=ticket.stem, sequence=attempt, surface="requisition_review", workspace=ctx.repo)
                result = StageResult(outcome="infra_error", artifact=None, findings=findings, cost=Cost(attempts=1))
                run = StagesRun(attempt=attempt, results={"implement": result}, ticket_sha=sha)
            else:
                ctx.driver.journal.append(
                    EventType.SIGNAL,
                    {
                        "signal": "requisition_verdict",
                        "verdict": review.verdict,
                        "findings": [{"code": f.code, "message": f.message} for f in review.findings],
                        "ticket_sha": sha,
                        "provider": review.provider,
                        "model": review.model,
                        "spec_version": review.spec_version,
                    },
                    ticket=ticket.stem,
                )
                if review.verdict != "approve" and not (review.verdict == "snag" and all(f.code == "render_feasibility" for f in review.findings)):
                    reason = "; ".join(f"[{f.code}] {f.message} ({f.paved_road})" for f in review.findings)
                    ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "premise_failed", "stage": "requisition", "reason": reason}, ticket=ticket.stem)
                    return "premise_failed"
    if run is None:
        run = await run_stages(ctx, ticket)
    if ctx.boundary.next_stage is not None:
        return "running"
    stage, result = run.last
    if findings := await ticket_change_findings(ctx, ticket.stem, expected=run.ticket_sha):
        result = StageResult(outcome="gate_failed", artifact=None, findings=findings, cost=result.cost)
    if stage == "review" and result.outcome == "ok":
        from chupa.mergequeue import ConflictHandoff

        with ctx.driver.stage(stem=ticket.stem, attempt=run.attempt, surface="merge") as event:
            stage, result = "merge", await (admission(ticket, attempt=run.attempt) if admission is not None else merge(ctx, ticket, attempt=run.attempt))
            event.end("conflict" if isinstance(result, ConflictHandoff) else result.outcome)
        if isinstance(result, ConflictHandoff):
            assert consume_handoff is not None
            return await consume_handoff(ticket, result, attempt=run.attempt)
        if result.outcome == "ok":
            return "merged"
    if result.outcome == "already_satisfied":
        ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": "already_satisfied", "stage": stage, "reason": "already_satisfied"}, ticket=ticket.stem)
        if ctx.worktree(ticket.stem).exists():
            await ctx.git.worktree_remove(ctx.repo, ctx.worktree(ticket.stem))
        return result.outcome
    await harvest_failure(ctx, ticket, attempt=run.attempt, stage=stage, outcome=result.outcome, findings=result.findings, results=(*run.results.values(),) + ((result,) if stage == "merge" else ()))
    if any(f.code == "ticket_changed" for f in result.findings):
        return await failure_terminal(ctx, ticket, outcome="gate_failed", stage=stage, findings=result.findings, attempt=run.attempt)
    drought = getattr(result, "provider_drought", None)
    quota = any(f.code == "quota_exhausted" for f in result.findings)
    if drought is not None or quota:
        return await failure_terminal(ctx, ticket, outcome=result.outcome, stage=stage, findings=result.findings, attempt=run.attempt, provider_drought=drought)
    if spent(ctx.config.caps, ctx.driver.journal.read(), ticket.stem, pending={"to": result.outcome}) == "attempts":
        return await failure_terminal(ctx, ticket, outcome=result.outcome, stage=stage, findings=result.findings, attempt=run.attempt)
    if result.outcome in {"infra_error", "timeout"}:
        ticket_sha = await ctx.git.rev_parse(ctx.repo, f"HEAD:{ticket_path(ticket.stem)}")
        consume(ctx.driver.journal, ticket.stem, "infra", ticket_sha)
    over_bound = result.outcome == "premise_failed" and any(f.code == "render_over_bound" for f in result.findings)
    if result.outcome == "premise_failed" and not over_bound:
        ticket_sha = await ctx.git.rev_parse(ctx.repo, f"HEAD:{ticket_path(ticket.stem)}")
        consume(ctx.driver.journal, ticket.stem, "premise_bounce", ticket_sha)
    diagnosed = result.outcome != "budget_exceeded" and not over_bound
    if diagnosed and isinstance(ctx.driver.llm, ProviderLLM) and not spent(ctx.config.caps, ctx.driver.journal.read(), ticket.stem) and ctx.worktree(ticket.stem).exists():
        tier, _ = capability(ticket, ctx.driver.journal.read())
        refusal = ctx.driver.llm.session.drought(ctx.config, tier, "diagnose")
        if refusal:
            return await failure_terminal(ctx, ticket, outcome="infra_error", stage=stage, findings=result.findings, attempt=run.attempt, provider_drought=refusal.record)
    if diagnosed:
        worktree = ctx.worktree(ticket.stem)
        mechanical = None if worktree.exists() else "workspace gone"
        if mechanical is None and (cap := spent(ctx.config.caps, ctx.driver.journal.read(), ticket.stem)):
            mechanical = spent_reason(cap)
        if mechanical is not None:
            if worktree.exists():
                diagnosis = await write_diagnosis(
                    ctx,
                    ticket,
                    attempt=run.attempt,
                    terminal=result.outcome,
                    stage=stage,
                    verdict="abandon-human",
                    lessons=[],
                    mechanical=mechanical,
                )
            else:
                # A lost workspace has no outbox; retain the mechanical verdict in the journal.
                diagnosis = None
            verdict = "abandon-human"
            lessons = []
        else:
            ticket_sha = await ctx.git.rev_parse(ctx.repo, f"HEAD:{ticket_path(ticket.stem)}")
            consume(ctx.driver.journal, ticket.stem, "diagnosis", ticket_sha)
            harvest_path = ctx.repo / "tickets" / ticket.stem / "attempts" / str(run.attempt) / "harvest.json"
            harvest_artifact = Harvest.model_validate_json(harvest_path.read_text()) if harvest_path.is_file() else None
            record_path = ctx.repo / "tickets" / ticket.stem / "run.md"
            material = DiagnosisMaterial(
                ticket=(ctx.repo / ticket_path(ticket.stem)).read_text(),
                terminal=result.outcome,
                stage=stage,
                harvest=harvest_artifact,
                run_record=record_path.read_text() if record_path.is_file() else None,
            )
            diagnosis = await diagnose(ctx, ticket, material, attempt=run.attempt)
            verdict, lessons = diagnosis.verdict, diagnosis.lessons
        ctx.driver.journal.append(
            EventType.SIGNAL,
            {"signal": "diagnosis", "attempt": run.attempt, "verdict": verdict, "lessons": lessons, "mechanical": mechanical if diagnosis is None else diagnosis.mechanical},
            ticket=ticket.stem,
        )
    reworked = None
    requested = over_bound or (diagnosed and verdict == "split")
    if requested and (over_bound or not spent(ctx.config.caps, ctx.driver.journal.read(), ticket.stem)):
        from chupa.daemon import apply_rework

        reworked = await apply_rework(ctx, ticket, result.findings, attempt=run.attempt)
    return await failure_terminal(
        ctx,
        ticket,
        outcome=result.outcome,
        stage=stage,
        findings=result.findings,
        attempt=run.attempt,
        reworked=reworked,
        rework_requested=requested,
        mechanical=over_bound,
        verdict=verdict if diagnosed else None,
    )


async def harvest_failure(ctx: StageContext, ticket: Ticket, *, attempt: int, stage: str, outcome: str, findings: list[Finding], results: tuple[StageResult, ...]) -> None:
    """A failed harvest never interrupts failure dispatch or the producing terminal."""
    if ctx.worktree(ticket.stem).exists():
        try:
            await harvest(ctx, ticket.stem, attempt=attempt, stage=stage, terminal=outcome, findings=findings, results=results)
        except Exception as exc:
            ctx.driver.journal.append(EventType.SIGNAL, {"signal": "harvest_failed", "error": ctx.driver.redactor.scrub(f"{type(exc).__name__}: {exc}")}, ticket=ticket.stem)


async def failure_terminal(
    ctx: StageContext,
    ticket: Ticket,
    *,
    outcome: str,
    stage: str,
    findings: list[Finding],
    attempt: int,
    reworked: StageResult | None = None,
    rework_requested: bool = False,
    mechanical: bool = False,
    verdict: str | None = None,
    provider_drought: dict | None = None,
) -> str:
    """Preserve the producing terminal, then retire a published split before wiping and returning."""
    from chupa.daemon import storm_producer
    from chupa.rework import ReworkOrder

    reason = ",".join(sorted({f.code for f in findings})) or outcome
    terminal = {"to": outcome, "stage": stage, "reason": reason}
    if provider_drought is None and reworked is not None:
        provider_drought = getattr(reworked, "provider_drought", None)
    if provider_drought is not None:
        terminal.update(to="infra_error", reason="provider_drought", provider_drought=provider_drought)
        rework_requested, verdict = False, None
        outcome = "infra_error"
    history = ctx.driver.journal.read()
    tier, effort = capability(ticket, history)
    split = False
    dispatch: JournalDispatch | None = "reject_queue" if any(f.code == "ticket_changed" for f in findings) else None
    if rework_requested:
        if reworked is not None and reworked.outcome == "ok":
            order = reworked.artifact
            assert isinstance(order, ReworkOrder)
            split = order.action == "split"
            verdict = "retry" if order.action == "update" else order.action
        else:
            verdict = "reject"
        if reworked is not None and (reworked.outcome != "ok" or (mechanical and verdict == "escalate")):
            extra = reworked.findings or [Finding(code="render_over_bound", message="Rework did not shrink the ticket", paved_road="shrink or split the committed ticket text and rerun drain")]
            if ctx.worktree(ticket.stem).exists():
                try:
                    await harvest(ctx, ticket.stem, attempt=attempt, stage=stage, terminal=outcome, findings=[*findings, *extra], results=(reworked,), kind="harvest-rework")
                except Exception:
                    storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock).enqueue(
                        message_class="failure_report",
                        origin=ticket.stem,
                        stage=stage,
                        outcome=outcome,
                        summary="; ".join(f"{f.message}; {f.paved_road}" for f in extra),
                        occurrence_id=arrival_id("rework-failure", ticket.stem, attempt, stage, outcome),
                    )
            else:
                storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock).enqueue(
                    message_class="failure_report",
                    origin=ticket.stem,
                    stage=stage,
                    outcome=outcome,
                    summary="; ".join(f"{f.message}; {f.paved_road}" for f in extra),
                    occurrence_id=arrival_id("rework-failure", ticket.stem, attempt, stage, outcome),
                )
    if not split and provider_drought is None and spent(ctx.config.caps, history, ticket.stem, pending=terminal) == "attempts":
        terminal["reason"] = spent_reason("attempts")
        dispatch = "reject_queue"
        mechanical = False
        verdict = "abandon-human"
    if not mechanical and not split and verdict is not None:
        previous = [e.body for e in history if e.type == EventType.STATE_TRANSITION and e.ticket == ticket.stem and e.body.get("to") in TERMINAL_STATES]
        match prior_dispatch := dispatch_of(previous[-1]) if previous else None:
            case "retry":
                identical = verdict == "retry" and previous[-1].get("reason") == reason
            case "escalate" | "reject_queue" | "spec_gap_hold" | None:
                identical = False
            case _:
                assert_never(prior_dispatch)
        identical = identical or (len(previous) >= IDENTICAL_K - 1 and all(e.get("reason") == reason for e in previous[-(IDENTICAL_K - 1) :]))
        # Reviewed updates have an explicit retry decision; the identical-wall rule belongs to diagnosis.
        if spent(ctx.config.caps, history, ticket.stem) or verdict in {"reject", "abandon-human"}:
            dispatch = "reject_queue"
        elif (
            verdict == "escalate"
            or (verdict == "retry" and outcome == "premise_failed" and stage == "implement" and not rework_requested)
            or (verdict is not None and identical and not rework_requested)
        ):
            rung = next_rung(ctx.config, tier, effort)
            if rung is None:
                dispatch = "reject_queue"
            else:
                dispatch = "escalate"
                terminal["rung"] = rung
        elif verdict == "retry":
            dispatch = "retry"
        elif verdict is not None:
            dispatch = "reject_queue"
    if dispatch is not None:
        terminal["dispatch"] = dispatch
    match terminal_dispatch := dispatch_of(terminal):
        case "reject_queue":
            routed = True
        case "retry" | "escalate" | "spec_gap_hold" | None:
            routed = bool(spent(ctx.config.caps, history, ticket.stem))
        case _:
            assert_never(terminal_dispatch)
    if not mechanical and not split and routed and provider_drought is None:
        terminal["routed"] = "reject_queue"
    ctx.driver.journal.append(EventType.STATE_TRANSITION, terminal, ticket=ticket.stem)
    if split:
        checkout = Checkout(ctx.repo, ctx.config, ctx.env, ctx.exec_, ctx.git, ctx.driver.journal, ctx.fs, ctx.driver.clock, ctx.driver.sleep)
        await reject_ticket(ticket.stem, checkout)
    if ctx.worktree(ticket.stem).exists():
        await ctx.git.worktree_remove(ctx.repo, ctx.worktree(ticket.stem))
    return "rejected" if split else outcome


async def harvest(
    ctx: StageContext,
    stem: str,
    *,
    attempt: int,
    stage: str | None,
    terminal: str,
    findings: list[Finding],
    results: tuple[StageResult, ...],
    kind: str = "harvest",
) -> None:
    """Extract the allowlisted failed-run record and lift it through the one outbox lane."""
    spool = ctx.config.state_dir / "spools" / stem / str(attempt)
    errors = list(spool.rglob("error.txt")) if spool.is_dir() else []
    newest_error = max(errors, key=lambda p: (p.stat().st_mtime_ns, str(p))) if errors else None
    reason = None if findings else (newest_error.read_text(errors="replace") if newest_error else terminal)
    # Prompts are inputs, not stage logs: Review's prompt carries the unreviewed code diff.
    logs = sorted(p for p in spool.rglob("*") if p.is_file() and p.name != "prompt.md") if spool.is_dir() else []
    stage_log_tail = "".join(p.read_text(errors="replace") for p in logs)[-HARVEST_TAIL_CHARS:]
    providers = ctx.config.state_dir / "spools" / "providers" / stem
    events = list(providers.rglob("events.jsonl")) if providers.is_dir() else []
    newest_events = max(events, key=lambda p: (p.stat().st_mtime_ns, str(p))) if events else None
    events_tail = (newest_events.read_text(errors="replace") if newest_events else "")[-HARVEST_TAIL_CHARS:]
    record = f"tickets/{stem}/run.md"
    artifact = Harvest(
        attempt=attempt,
        stage=stage,
        terminal=terminal,
        findings=findings,
        reason=reason,
        diff_stat=await ctx.git.diff_stat(ctx.repo, "main", stem),
        stage_log_tail=stage_log_tail,
        events_tail=events_tail,
        wall_seconds=sum(r.cost.seconds for r in results) if results else None,
        usd=sum(r.cost.usd for r in results) if results else None,
        run_record=record if (ctx.repo / record).is_file() else None,
    )
    path = ctx.worktree(stem) / "tickets" / stem / "attempts" / str(attempt) / "harvest.json"
    ctx.fs.write(path, (artifact.model_dump_json(indent=2) + "\n").encode())
    await lift_outbox(ctx, stem, kind, attempt=attempt, only=f"attempts/{attempt}/harvest.json")


async def harvest_orphan(checkout: Checkout, stem: str, attempt: int) -> None:
    """Use the run-terminal harvest with an effects context; an orphan makes no model call."""
    driver = Driver.from_config(checkout.config, llm=cast(LLM, None), env=checkout.env, clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
    driver.journal = checkout.journal
    driver.effects = Effects(checkout.journal)
    ctx = StageContext(repo=checkout.repo, config=checkout.config, env=checkout.env, exec_=checkout.exec_, git=checkout.git, fs=checkout.fs, driver=driver, specs_dir=SPECS_DIR)
    await harvest(ctx, stem, attempt=attempt, stage=None, terminal="abandoned", findings=[], results=())


async def reap(checkout: Checkout) -> list[str]:
    assert checkout.config.worktree_root is not None
    return await reconcile(checkout.journal, checkout.git, checkout.repo, checkout.config.worktree_root, lambda orphan, attempt: harvest_orphan(checkout, orphan, attempt))


async def run_ticket(stem: str, checkout: Checkout, dispatch: Dispatch) -> int:
    if findings := stem_findings(stem):
        raise Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, verb="run", instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    log = EngineLog(checkout.config.state_dir / "engine.log", Redactor.from_config(checkout.config, checkout.env), checkout.clock)
    pid = os.getpid()
    lock.acquire()
    outcome = "parked"
    try:
        log.event("engine_start", verb="run", pid=pid)
        await reap(checkout)
        if checkout.control is not None:
            checkout.control.providers.timers.reconstruct()
            checkout.control.providers.timers.fire_due()
        if hasattr(dispatch, "prepare"):
            await dispatch.prepare()
        from chupa.daemon import storm_producer

        storm_producer(root=checkout.config.state_dir / BOX_DIR, fs=checkout.fs, journal=checkout.journal, clock=checkout.clock).recover()
        ticket = await _admit(stem, checkout)
        if checkout.control is not None:
            tier, _ = capability(ticket, checkout.journal.read())
            drought = checkout.control.providers.drought(checkout.config, tier, "implement")
            if drought:
                checkout.control.providers.park(stem, drought)
                return EXIT_TICKET
        ticket_sha = await checkout.git.rev_parse(checkout.repo, f"main:{ticket_path(stem)}")
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": ticket_sha}, ticket=stem)
        terminal = await dispatch(ticket)
        if terminal not in TERMINAL_STATES:
            raise ValueError(f"stage seam returned {terminal!r}, not a terminal state {sorted(TERMINAL_STATES)}")
        outcome = terminal
        return EXIT_MERGED if terminal == "merged" else EXIT_TICKET
    finally:
        try:
            if checkout.control is not None:
                await checkout.control.providers.close()
        finally:
            try:
                exc = sys.exception()
                log.event("engine_stop", verb="run", pid=pid, outcome=f"error: {type(exc).__name__}" if exc else outcome)
            finally:
                lock.release()


async def ticket_pending(git, repo, stem: str) -> bool:
    return bool(await git.status_porcelain(repo, "--untracked-files=all", "--", f"tickets/{stem}/"))


async def verdict(stem: str, checkout: Checkout, *, kill: bool, extension: bool = False) -> int:
    """Resolve a draft or Reject item while holding the same writer lock as run and drain."""
    if findings := stem_findings(stem):
        raise Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, verb="reject" if kill else "confirm", instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    lock.acquire()
    try:
        await reap(checkout)
        return await verdict_locked(stem, checkout, kill=kill, extension=extension)
    finally:
        lock.release()


async def verdict_locked(stem: str, checkout: Checkout, *, kill: bool, extension: bool = False) -> int:
    """Apply verdict rules with the writer lock already held."""
    intake_result = await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs, stems={stem})
    if refused := intake_result.refused.get(stem):
        raise Refusal(f"{ticket_path(stem)} failed intake: " + "; ".join(f.message for f in refused), "fix the ticket and retry the verdict")
    history = checkout.journal.read()
    rel = ticket_path(stem)
    path = checkout.repo / rel
    if not path.is_file() and not any(e.ticket == stem for e in history):
        raise Refusal(f"unknown stem {stem}", "name a journaled stem or an existing ticket.md")
    draft = path.is_file() and _ticket_state(path) == "draft"
    refusal = verdict_refusal(history, stem, kill, draft, set())
    # Preserve the command-line repeat-keep refusal's precedence over queue admission.
    if refusal and (kill or draft or refusal[0].endswith("is running")):
        raise Refusal(*refusal)
    if kill:
        changed = await reject_ticket(stem, checkout)
        print(f"rejected {stem}" if changed else f"already rejected {stem}")
        return EXIT_MERGED
    if draft:
        checkout.fs.write(path, stamp(path.read_text(), "state", "confirmed").encode())
        sha = await checkout.git.commit(checkout.repo, f"chupa({stem}): confirmed", only=[rel])
        checkout.journal.append(EventType.SIGNAL, {"signal": "draft_confirmed", "commit": sha}, ticket=stem)
        print(f"confirmed draft {stem}")
        return EXIT_MERGED
    ticket_sha = await checkout.git.rev_parse(checkout.repo, f"HEAD:{rel}") if path.is_file() else None
    prior_keep = next(
        (
            e
            for e in reversed(history)
            if e.type == EventType.SIGNAL and e.ticket == stem and e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "keep" and e.body.get("actor") == "operator"
        ),
        None,
    )
    if not extension and prior_keep is not None and prior_keep.body.get("ticket_sha") == ticket_sha:
        raise Refusal(f"{stem} was already kept at this ticket content", "edit the ticket before re-enqueueing")
    if refusal:
        raise Refusal(*refusal)
    checkout.journal.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "keep", "actor": "operator", "ticket_sha": ticket_sha}, ticket=stem)
    print(f"kept {stem}")
    return EXIT_MERGED


async def reject_ticket(stem: str, checkout: Checkout) -> bool:
    """Reject mutation for a caller already holding the writer lock."""
    rel = ticket_path(stem)
    path = checkout.repo / rel
    last = last_states(checkout.journal.read()).get(stem)
    if path.is_file() and _ticket_state(path) != "rejected":
        checkout.fs.write(path, stamp(path.read_text(), "state", "rejected").encode())
        await checkout.git.commit(checkout.repo, f"chupa({stem}): rejected", only=[rel])
    if last != "rejected":
        checkout.journal.append(EventType.SIGNAL, {"signal": "reject_verdict", "verdict": "kill", "actor": "operator"}, ticket=stem)
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket=stem)
    await _dead_dependents(stem, checkout)
    return last != "rejected"


def _ticket_state(path: Path) -> str | None:
    split = split_frontmatter(path.read_text())
    return yaml.safe_load(split[0]).get("state") if split else None


async def _dead_dependents(dead: str, checkout: Checkout) -> None:
    history = checkout.journal.read()
    from chupa.rework import dead_dependencies

    last = last_states(history)
    deaths = dead_dependencies(history)
    from chupa.daemon import storm_producer

    box = storm_producer(root=checkout.config.state_dir / BOX_DIR, fs=checkout.fs, journal=checkout.journal, clock=checkout.clock)
    for path in sorted((checkout.repo / "tickets").glob("*/ticket.md")):
        stem = path.parent.name
        if stem == dead or _ticket_state(path) != "confirmed" or last.get(stem) in SETTLED | {"rejected"}:
            continue
        try:
            ticket = parse_ticket(stem, path.read_text(), checkout.repo)
        except TicketInvalid:
            continue
        for dependency in sorted(set(ticket.depends) & deaths):
            if not any(e.type == EventType.SIGNAL and e.ticket == stem and e.body.get("signal") == "dead_dependency" and e.body.get("dead") == dependency for e in history):
                box.enqueue(
                    message_class="failure_report",
                    origin=stem,
                    stage="depends",
                    outcome="rejected",
                    summary=f"{stem} depends on {dependency}, which was rejected or abandoned; re-wire, re-scope, or reject it",
                    occurrence_id=arrival_id("dead-dependency", stem, dependency),
                )
                checkout.journal.append(EventType.SIGNAL, {"signal": "dead_dependency", "dead": dependency}, ticket=stem)


async def _admit(stem: str, checkout: Checkout) -> Ticket:
    """Intake the named ticket, then validate it for dispatch; refuse anything not dispatchable."""
    repo = checkout.repo
    result = await intake(repo, checkout.git, checkout.journal, checkout.fs, stems={stem})
    path = repo / ticket_path(stem)
    exists = path.is_file()
    ticket = None
    # Intake refusal precedes disk validation, which precedes dispatch state checks.
    if exists and not result.refused.get(stem):
        try:
            ticket = validate_ticket(stem, path.read_text(), repo)
        except TicketInvalid as exc:
            ticket = exc.findings
    history = checkout.journal.read() if ticket is not None and not isinstance(ticket, list) else ()
    admission = run_admission(stem, history, exists, ticket, result.refused.get(stem))
    if admission.outcome == "refuse":
        raise Refusal(admission.message, admission.paved_road)
    return ticket


async def apply_admission(stem, verb, key, actor, c):
    events = c.journal.read()
    intents = [i for i, e in enumerate(events) if e.type == EventType.EFFECT_INTENT and e.key == key]
    since = events[intents[0] + 1 :] if intents else []
    # A request-specific baseline is journaled before any ticket mutation.
    baseline_key = key + "/baseline"
    baselines = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION and e.key == baseline_key]

    async def baseline():
        return await c.git.rev_parse(c.repo, "HEAD")

    base = baselines[0] if baselines else await Effects(c.journal).run(baseline, key=baseline_key, ticket=stem)
    signals = [e for e in since if e.ticket == stem]
    path = c.repo / ticket_path(stem)
    if baselines and len(intents) > 1 and path.is_file() and await c.git.rev_parse(c.repo, "HEAD") == base:
        try:
            committed = await c.git._run(c.repo, "show", f"{base}:{ticket_path(stem)}")
        except GitError:
            committed = None
        state = "rejected" if verb == "reject" else "confirmed"
        if committed is not None and path.read_text() != committed and path.read_text() == stamp(committed, "state", state):
            await c.git.commit(c.repo, f"chupa({stem}): {state}", only=[str(ticket_path(stem))])
    if verb == "confirm":
        applied = any(e.body.get("signal") in ("draft_confirmed", "reject_verdict") and (e.body.get("signal") != "reject_verdict" or e.body.get("verdict") == "keep") for e in signals)
        if not applied:
            log = await c.git._run(c.repo, "log", "--format=%H%x00%s", f"{base}..HEAD", "--", str(ticket_path(stem)))
            commits = [line.split("\0", 1) for line in log.splitlines() if "\0" in line]
            confirmed = next((sha for sha, message in commits if message == f"chupa({stem}): confirmed"), None)
            if confirmed:
                c.journal.append(EventType.SIGNAL, {"signal": "draft_confirmed", "commit": confirmed}, ticket=stem)
                applied = True
    else:
        applied = any(e.type == EventType.STATE_TRANSITION and e.body.get("to") == "rejected" for e in signals)
        killed = any(e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "kill" for e in signals)
        if killed and not applied:
            c.journal.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket=stem)
            applied = True
        if applied:
            await _dead_dependents(stem, c)
    refusal = None
    if not applied:
        try:
            await verdict_locked(stem, c, kill=verb == "reject", extension=actor == "extension")
        except Refusal as exc:
            refusal = str(exc)
    return {"refusal": refusal}
