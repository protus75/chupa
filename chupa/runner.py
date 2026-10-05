"""The `run <stem>` scaffold verb (CHUPA_PLAN.md sections 11.2, 18, 19.P1): one ticket through intake, the
single-writer lockfile, and the stage-dispatch seam, all in the one process holding the lock.

Exit codes (section 18): 0 merged, 1 a non-ok ticket terminal, 2 an engine-plane refusal.
"""

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from chupa.artifacts import Finding, Harvest, StageResult
from chupa.caps import consume
from chupa.config import Config
from chupa.driver import Driver
from chupa.git import Git
from chupa.journal import TERMINAL_STATES, EventType, Journal
from chupa.llm import LLM
from chupa.lockfile import Lockfile
from chupa.merge import merge
from chupa.providers import ProviderLLM
from chupa.reconcile import reconcile
from chupa.seams import Clock, FileSystem, GroupExec
from chupa.stages import StageContext, lift_outbox, run_stages
from chupa.status import last_states
from chupa.tickets import Ticket, TicketInvalid, intake, stem_findings, ticket_path, validate_ticket

EXIT_MERGED = 0
EXIT_TICKET = 1
EXIT_REFUSED = 2

# Engine plane: the prompt specs ship with the engine, not the host checkout it runs against.
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
CALL_TIMEOUT_S = 900.0
HARVEST_TAIL_CHARS = 4_000

# The stage seam: drives the validated ticket through the stages and merge, journals the run's single
# terminal transition (section 11), and returns that terminal state.
Dispatch = Callable[[Ticket], Awaitable[str]]


class Refusal(Exception):
    """An engine-plane refusal (exit 2): nothing was dispatched."""

    def __init__(self, message: str, paved_road: str) -> None:
        super().__init__(f"{message} -- {paved_road}")


@dataclass(frozen=True)
class Checkout:
    """The composed seams one invocation runs against; the stage pipeline is built from it."""

    repo: Path
    config: Config
    env: Mapping[str, str]
    exec_: GroupExec
    git: Git
    journal: Journal
    fs: FileSystem
    clock: Clock


Pipeline = Callable[[Checkout], Dispatch]


def pipeline(checkout: Checkout) -> Dispatch:
    """The production stage-seam binding: the configured providers serve every call."""
    llm = ProviderLLM(checkout.config, exec_=checkout.exec_, fs=checkout.fs, env=checkout.env,
                      cwd=checkout.repo, timeout=CALL_TIMEOUT_S)
    return bind(checkout, llm)


def bind(checkout: Checkout, llm: LLM) -> Dispatch:
    driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock,
                                sleep=asyncio.sleep, fs=checkout.fs)
    ctx = StageContext(repo=checkout.repo, config=checkout.config, env=checkout.env, exec_=checkout.exec_,
                       git=checkout.git, fs=checkout.fs, driver=driver, specs_dir=SPECS_DIR)
    return lambda ticket: drive(ctx, ticket)


async def drive(ctx: StageContext, ticket: Ticket) -> str:
    """Implement -> Check -> Review -> Merge; harvest, dispatch, journal, then wipe a non-ok run."""
    run = await run_stages(ctx, ticket)
    stage, result = run.last
    if stage == "review" and result.outcome == "ok":
        stage, result = "merge", await merge(ctx, ticket, attempt=run.attempt)
        if result.outcome == "ok":
            return "merged"
    if ctx.worktree(ticket.stem).exists() and result.outcome != "already_satisfied":
        try:
            await harvest(ctx, ticket.stem, attempt=run.attempt, stage=stage, terminal=result.outcome,
                          findings=result.findings, results=(*run.results.values(),)
                          + ((result,) if stage == "merge" else ()))
        except Exception as e:
            ctx.driver.journal.append(EventType.SIGNAL,
                                      {"signal": "harvest_failed", "error": f"{type(e).__name__}: {e}"},
                                      ticket=ticket.stem)
    if result.outcome in {"infra_error", "timeout"}:
        ticket_sha = await ctx.git.rev_parse(ctx.repo, f"HEAD:{ticket_path(ticket.stem)}")
        consume(ctx.driver.journal, ticket.stem, "infra", ticket_sha)
    ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": result.outcome, "stage": stage}, ticket=ticket.stem)
    if ctx.worktree(ticket.stem).exists():
        await ctx.git.worktree_remove(ctx.repo, ctx.worktree(ticket.stem))
    return result.outcome


async def harvest(
    ctx: StageContext, stem: str, *, attempt: int, stage: str | None, terminal: str,
    findings: list[Finding], results: tuple[StageResult, ...],
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
        attempt=attempt, stage=stage, terminal=terminal, findings=findings, reason=reason,
        diff_stat=await ctx.git.diff_stat(ctx.repo, "main", stem),
        stage_log_tail=stage_log_tail, events_tail=events_tail,
        wall_seconds=sum(r.cost.seconds for r in results) if results else None,
        usd=sum(r.cost.usd for r in results) if results else None,
        run_record=record if (ctx.repo / record).is_file() else None,
    )
    path = ctx.worktree(stem) / "tickets" / stem / "attempts" / str(attempt) / "harvest.json"
    ctx.fs.write(path, (artifact.model_dump_json(indent=2) + "\n").encode())
    await lift_outbox(ctx, stem, "harvest", attempt=attempt, only=f"attempts/{attempt}/harvest.json")


async def run_ticket(stem: str, checkout: Checkout, dispatch: Dispatch) -> int:
    if findings := stem_findings(stem):
        raise Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo),
                    clock=checkout.clock)
    lock.acquire()
    try:
        assert checkout.config.worktree_root is not None  # resolved at config load
        await reconcile(checkout.journal, checkout.git, checkout.repo, checkout.config.worktree_root)
        ticket = await _admit(stem, checkout)
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket=stem)
        terminal = await dispatch(ticket)
        if terminal not in TERMINAL_STATES:
            raise ValueError(f"stage seam returned {terminal!r}, not a terminal state {sorted(TERMINAL_STATES)}")
        return EXIT_MERGED if terminal == "merged" else EXIT_TICKET
    finally:
        lock.release()


async def _admit(stem: str, checkout: Checkout) -> Ticket:
    """Intake every pending ticket, then validate the one to dispatch; refuse anything not dispatchable."""
    repo = checkout.repo
    result = await intake(repo, checkout.git, checkout.journal, checkout.fs)
    if refused := result.refused.get(stem):
        raise Refusal(f"{ticket_path(stem)} failed intake: "
                      + "; ".join(f"[{f.code}] {f.message} ({f.paved_road})" for f in refused),
                      f"fix the ticket, then `run {stem}` again")
    path = repo / ticket_path(stem)
    if not path.is_file():
        raise Refusal(f"{ticket_path(stem)} does not exist",
                      f"author it with `python -m chupa new {stem}`, fill it, then `run {stem}`")
    try:
        ticket = validate_ticket(stem, path.read_text(), repo)
    except TicketInvalid as e:
        raise Refusal(f"{ticket_path(stem)} is invalid: "
                      + "; ".join(f"[{f.code}] {f.message} ({f.paved_road})" for f in e.findings),
                      f"fix the ticket, then `run {stem}` again") from None
    last = last_states(checkout.journal.read())
    if last.get(stem) == "merged" or ticket.frontmatter.state == "merged":
        raise Refusal(f"{stem} is already merged", "author follow-up work as a new stem with `new`")
    if ticket.frontmatter.state != "confirmed":
        raise Refusal(f"{stem} is `state: {ticket.frontmatter.state}`, not confirmed",
                      f"set `state: confirmed` in {ticket_path(stem)} to dispatch it, or author a new stem")
    if unmerged := [d for d in ticket.depends if last.get(d) != "merged"]:
        raise Refusal(f"{stem} depends on unmerged {', '.join(unmerged)}",
                      " then ".join(f"`run {d}`" for d in unmerged) + f" first, then `run {stem}`")
    return ticket
