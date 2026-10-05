"""The `run <stem>` scaffold verb (CHUPA_PLAN.md sections 11.2, 18, 19.P1): one ticket through intake, the
single-writer lockfile, and the stage-dispatch seam, all in the one process holding the lock.

Exit codes (section 18): 0 merged, 1 a non-ok ticket terminal, 2 an engine-plane refusal.
"""

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from chupa.config import Config
from chupa.driver import Driver
from chupa.git import Git
from chupa.journal import TERMINAL_STATES, EventType, Journal
from chupa.llm import LLM
from chupa.lockfile import Lockfile
from chupa.merge import merge
from chupa.providers import ProviderLLM
from chupa.seams import Clock, FileSystem, GroupExec
from chupa.stages import StageContext, run_stages
from chupa.status import last_states
from chupa.tickets import Ticket, TicketInvalid, intake, stem_findings, ticket_path, validate_ticket

EXIT_MERGED = 0
EXIT_TICKET = 1
EXIT_REFUSED = 2

# Engine plane: the prompt specs ship with the engine, not the host checkout it runs against.
SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"
CALL_TIMEOUT_S = 900.0

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
    """Implement -> Check -> Review -> Merge; journal a non-ok terminal (merge journals `merged` itself).

    Phase 1 has no retry, diagnosis, or harvest (Phase 2): a non-ok terminal leaves the ticket, branch,
    and worktree in place for the operator, and the stem stays eligible for a fresh `run`.
    """
    run = await run_stages(ctx, ticket)
    stage, result = run.last
    if stage == "review" and result.outcome == "ok":
        stage, result = "merge", await merge(ctx, ticket, attempt=run.attempt)
        if result.outcome == "ok":
            return "merged"
    ctx.driver.journal.append(EventType.STATE_TRANSITION, {"to": result.outcome, "stage": stage}, ticket=ticket.stem)
    return result.outcome


async def run_ticket(stem: str, checkout: Checkout, dispatch: Dispatch) -> int:
    if findings := stem_findings(stem):
        raise Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo),
                    clock=checkout.clock)
    lock.acquire()
    try:
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
