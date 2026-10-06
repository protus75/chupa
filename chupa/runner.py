"""The `run <stem>` scaffold verb (CHUPA_PLAN.md sections 11.2, 18, 19.P1): one ticket through intake, the
single-writer lockfile, and the stage-dispatch seam, all in the one process holding the lock.

Exit codes (section 18): 0 merged, 1 a non-ok ticket terminal, 2 an engine-plane refusal.
"""

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

import yaml

from chupa.artifacts import Finding, Harvest, StageResult
from chupa.box import BOX_DIR, Box
from chupa.caps import capability, consume, next_rung, spent, spent_reason
from chupa.config import Config
from chupa.driver import Driver
from chupa.git import Git
from chupa.journal import TERMINAL_STATES, EventType, Journal
from chupa.llm import LLM
from chupa.lockfile import Lockfile
from chupa.merge import merge
from chupa.providers import ProviderLLM
from chupa.reconcile import reconcile
from chupa.seams import Clock, FileSystem, GroupExec, Sleep
from chupa.stages import DiagnosisMaterial, StageContext, diagnose, lift_outbox, run_stages, write_diagnosis
from chupa.status import last_states, reject_queue
from chupa.tickets import (Ticket, TicketInvalid, intake, parse_ticket, split_frontmatter, stamp,
                           stem_findings, ticket_path, validate_ticket)

EXIT_MERGED = 0
EXIT_TICKET = 1
EXIT_REFUSED = 2

# Engine plane: the prompt specs ship with the engine, not the host checkout it runs against.
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
CALL_TIMEOUT_S = 900.0
HARVEST_TAIL_CHARS = 4_000
IDENTICAL_K = 3

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
    sleep: Sleep = asyncio.sleep


Pipeline = Callable[[Checkout], Dispatch]


def pipeline(checkout: Checkout) -> Dispatch:
    """The production stage-seam binding: the configured providers serve every call."""
    llm = ProviderLLM(checkout.config, exec_=checkout.exec_, fs=checkout.fs, env=checkout.env,
                      cwd=checkout.repo, timeout=CALL_TIMEOUT_S)
    return bind(checkout, llm)


def bind(checkout: Checkout, llm: LLM) -> Dispatch:
    driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock,
                                sleep=checkout.sleep, fs=checkout.fs)
    ctx = StageContext(repo=checkout.repo, config=checkout.config, env=checkout.env, exec_=checkout.exec_,
                       git=checkout.git, fs=checkout.fs, driver=driver, specs_dir=SPECS_DIR)
    return lambda ticket: drive(ctx, ticket)


async def drive(ctx: StageContext, ticket: Ticket) -> str:
    """Implement -> Check -> Review -> Merge; harvest, dispatch, journal, then wipe a non-ok run."""
    tier, effort = capability(ticket, ctx.driver.journal.read())
    ticket = replace(ticket, frontmatter=ticket.frontmatter.model_copy(
        update={"agent_tier": tier, "agent_effort": effort}))
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
    over_bound = result.outcome == "premise_failed" and any(
        f.code == "render_over_bound" for f in result.findings)
    if result.outcome == "premise_failed" and not over_bound:
        ticket_sha = await ctx.git.rev_parse(ctx.repo, f"HEAD:{ticket_path(ticket.stem)}")
        consume(ctx.driver.journal, ticket.stem, "premise_bounce", ticket_sha)
    diagnosed = result.outcome != "budget_exceeded" and not over_bound
    if diagnosed:
        worktree = ctx.worktree(ticket.stem)
        mechanical = None if worktree.exists() else "workspace gone"
        if mechanical is None and (cap := spent(ctx.config.caps, ctx.driver.journal.read(), ticket.stem)):
            mechanical = spent_reason(cap)
        if mechanical is not None:
            if worktree.exists():
                diagnosis = await write_diagnosis(
                    ctx, ticket, attempt=run.attempt, terminal=result.outcome, stage=stage,
                    verdict="abandon-human", lessons=[], mechanical=mechanical,
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
                ticket=(ctx.repo / ticket_path(ticket.stem)).read_text(), terminal=result.outcome, stage=stage,
                harvest=harvest_artifact, run_record=record_path.read_text() if record_path.is_file() else None,
            )
            diagnosis = await diagnose(ctx, ticket, material, attempt=run.attempt)
            verdict, lessons = diagnosis.verdict, diagnosis.lessons
        ctx.driver.journal.append(EventType.SIGNAL,
                                  {"signal": "diagnosis", "attempt": run.attempt, "verdict": verdict,
                                   "lessons": lessons, "mechanical": mechanical if diagnosis is None else diagnosis.mechanical},
                                  ticket=ticket.stem)
    reason = ",".join(sorted({f.code for f in result.findings})) or result.outcome
    terminal = {"to": result.outcome, "stage": stage, "reason": reason}
    history = ctx.driver.journal.read()
    if diagnosed:
        previous = [e.body for e in history if e.type == EventType.STATE_TRANSITION
                    and e.ticket == ticket.stem and e.body.get("to") in TERMINAL_STATES]
        identical = (verdict == "retry" and bool(previous)
                     and previous[-1].get("dispatch") == "retry" and previous[-1].get("reason") == reason)
        identical = identical or (len(previous) >= IDENTICAL_K - 1 and all(
            e.get("reason") == reason for e in previous[-(IDENTICAL_K - 1):]))
        if spent(ctx.config.caps, history, ticket.stem) or verdict in {"split", "reject", "abandon-human"}:
            terminal["dispatch"] = "reject_queue"
        elif verdict == "escalate" or identical:
            rung = next_rung(ctx.config, tier, effort)
            if rung is None:
                terminal["dispatch"] = "reject_queue"
            else:
                terminal["dispatch"] = "escalate"
                terminal["rung"] = rung
        elif verdict == "retry":
            terminal["dispatch"] = "retry"
        else:
            terminal["dispatch"] = "reject_queue"
    if terminal.get("dispatch") == "reject_queue" or (not over_bound and spent(ctx.config.caps, history, ticket.stem)):
        terminal["routed"] = "reject_queue"
    ctx.driver.journal.append(EventType.STATE_TRANSITION, terminal, ticket=ticket.stem)
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


async def harvest_orphan(checkout: Checkout, stem: str, attempt: int) -> None:
    """Use the run-terminal harvest with an effects context; an orphan makes no model call."""
    driver = Driver.from_config(checkout.config, llm=cast(LLM, None), env=checkout.env,
                                clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
    ctx = StageContext(repo=checkout.repo, config=checkout.config, env=checkout.env, exec_=checkout.exec_,
                       git=checkout.git, fs=checkout.fs, driver=driver, specs_dir=SPECS_DIR)
    await harvest(ctx, stem, attempt=attempt, stage=None, terminal="abandoned", findings=[], results=())


async def run_ticket(stem: str, checkout: Checkout, dispatch: Dispatch) -> int:
    if findings := stem_findings(stem):
        raise Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo),
                    clock=checkout.clock)
    lock.acquire()
    try:
        assert checkout.config.worktree_root is not None  # resolved at config load
        await reconcile(checkout.journal, checkout.git, checkout.repo, checkout.config.worktree_root,
                        lambda orphan, attempt: harvest_orphan(checkout, orphan, attempt))
        ticket = await _admit(stem, checkout)
        checkout.journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket=stem)
        terminal = await dispatch(ticket)
        if terminal not in TERMINAL_STATES:
            raise ValueError(f"stage seam returned {terminal!r}, not a terminal state {sorted(TERMINAL_STATES)}")
        return EXIT_MERGED if terminal == "merged" else EXIT_TICKET
    finally:
        lock.release()


async def verdict(stem: str, checkout: Checkout, *, kill: bool) -> int:
    """Resolve a draft or Reject item while holding the same writer lock as run and drain."""
    if findings := stem_findings(stem):
        raise Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo),
                    clock=checkout.clock)
    lock.acquire()
    try:
        intake_result = await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs)
        if refused := intake_result.refused.get(stem):
            raise Refusal(f"{ticket_path(stem)} failed intake: " + "; ".join(f.message for f in refused),
                          "fix the ticket and retry the verdict")
        history = checkout.journal.read()
        rel = ticket_path(stem)
        path = checkout.repo / rel
        if not path.is_file() and not any(e.ticket == stem for e in history):
            raise Refusal(f"unknown stem {stem}", "name a journaled stem or an existing ticket.md")
        last = last_states(history).get(stem)
        if last == "running":
            raise Refusal(f"{stem} is running", "wait for its terminal, then retry")
        if kill:
            if last in {"merged", "already_satisfied"}:
                raise Refusal(f"{stem} is settled", "leave settled work in place")
            if path.is_file() and _ticket_state(path) != "rejected":
                checkout.fs.write(path, stamp(path.read_text(), "state", "rejected").encode())
                await checkout.git.add(checkout.repo, [rel])
                await checkout.git.commit(checkout.repo, f"chupa({stem}): rejected", only=[rel])
            await _dead_dependents(stem, checkout)
            if last != "rejected":
                checkout.journal.append(EventType.SIGNAL,
                                        {"signal": "reject_verdict", "verdict": "kill", "actor": "operator"},
                                        ticket=stem)
                checkout.journal.append(EventType.STATE_TRANSITION, {"to": "rejected"}, ticket=stem)
                print(f"rejected {stem}")
            else:
                print(f"already rejected {stem}")
            return EXIT_MERGED
        if path.is_file() and _ticket_state(path) == "draft":
            checkout.fs.write(path, stamp(path.read_text(), "state", "confirmed").encode())
            await checkout.git.add(checkout.repo, [rel])
            await checkout.git.commit(checkout.repo, f"chupa({stem}): confirmed", only=[rel])
            sha = await checkout.git.rev_parse(checkout.repo, "HEAD")
            checkout.journal.append(EventType.SIGNAL, {"signal": "draft_confirmed", "commit": sha}, ticket=stem)
            print(f"confirmed draft {stem}")
            return EXIT_MERGED
        ticket_sha = await checkout.git.rev_parse(checkout.repo, f"HEAD:{rel}") if path.is_file() else None
        prior_keep = next((e for e in reversed(history) if e.type == EventType.SIGNAL and e.ticket == stem
                           and e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "keep"
                           and e.body.get("actor") == "operator"), None)
        if prior_keep is not None and prior_keep.body.get("ticket_sha") == ticket_sha:
            raise Refusal(f"{stem} was already kept at this ticket content",
                          "edit the ticket (or fix the plan and regenerate it) before re-enqueueing")
        if stem not in reject_queue(history):
            raise Refusal(f"{stem} is neither a draft nor in the Reject queue",
                          "run `status` to list the Reject queue")
        checkout.journal.append(EventType.SIGNAL,
                                {"signal": "reject_verdict", "verdict": "keep", "actor": "operator",
                                 "ticket_sha": ticket_sha}, ticket=stem)
        print(f"kept {stem}")
        return EXIT_MERGED
    finally:
        lock.release()


def _ticket_state(path: Path) -> str | None:
    split = split_frontmatter(path.read_text())
    return yaml.safe_load(split[0]).get("state") if split else None


async def _dead_dependents(dead: str, checkout: Checkout) -> None:
    history = checkout.journal.read()
    last = last_states(history)
    box = Box(checkout.config.state_dir / BOX_DIR, checkout.fs)
    for path in sorted((checkout.repo / "tickets").glob("*/ticket.md")):
        stem = path.parent.name
        if stem == dead or _ticket_state(path) != "confirmed" or last.get(stem) in {"merged", "already_satisfied", "rejected"}:
            continue
        ticket = parse_ticket(stem, path.read_text(), checkout.repo,
                              plan=(checkout.repo / "CHUPA_PLAN.md").read_text())
        if dead not in ticket.depends:
            continue
        if not any(e.type == EventType.SIGNAL and e.ticket == stem
                   and e.body.get("signal") == "dead_dependency" and e.body.get("dead") == dead
                   for e in history):
            checkout.journal.append(EventType.SIGNAL, {"signal": "dead_dependency", "dead": dead}, ticket=stem)
        box.enqueue(message_class="failure_report", origin=stem, stage="depends", outcome="rejected",
                    summary=f"{stem} depends on {dead}, which was rejected; re-wire, re-scope, or reject it")


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
