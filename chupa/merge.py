"""Merge: the single-admission writer to main (CHUPA_PLAN.md sections 7, 9, 10; 19.P1).

Per admission, all before main moves: restore the worktree's ticket plane -> rebase onto main ->
re-run the mechanical hard set on the rebased candidate -> require the pinned review approval ->
squash-merge with trailers -> journal `to: merged` -> delete the worktree and branch. Runs inline
in the one CLI process holding the single-writer lock; the serial merge task, red-streak pause, and
tree-hash assert are Phase 3. The bug gate is deferred to its first bug-intake consumer (Phase 6).

A refusal leaves main untouched and the branch in place; journaling a non-ok terminal is the
runner's (section 11.2).
"""

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from chupa.artifacts import Artifact, Cost, Finding, NonBlank, StageResult
from chupa.gates import GateReport, run_gates
from chupa.git import RebaseRefused
from chupa.journal import EventType
from chupa.stages import (
    CHECK_GATES,
    MAIN,
    ApprovedInvoice,
    StageContext,
    check_severity,
    gather_evidence,
    read_review,
)
from chupa.tickets import TICKETS_DIR, Ticket, TicketInvalid, ticket_path, validate_ticket

# Versions the merge contract in the provenance slot, like the mechanical Check.
MERGE_SPEC_VERSION = 1


class Candidate(BaseModel):
    """What the merge-only gates judge: the rebased branch plus main's ticket and pinned review."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    stem: NonBlank
    reviewed_sha: NonBlank  # the branch head Review saw, before the rebase
    changed_files: list[str]
    ticket_text: str
    review_text: str | None  # main's `review.md`, None when absent


class Admission(Artifact):
    """Merge's artifact: the squash commit on main and the approval it carried."""

    stem: NonBlank
    commit: NonBlank
    reviewed_sha: NonBlank


class TicketSchemaGate:
    """Main's `ticket.md` still passes the section 13 grammar: a hand edit mid-run is re-judged here."""

    code = "ticket_schema"

    def check(self, artifact: Candidate, workspace: Path) -> GateReport:
        try:
            validate_ticket(artifact.stem, artifact.ticket_text, workspace)
        except TicketInvalid as e:
            return GateReport(code=self.code, verdict="fail",
                              findings=[f.model_copy(update={"code": self.code}) for f in e.findings])
        return GateReport(code=self.code, verdict="pass")


class PostRebaseGate:
    """The branch carries code only (section 10): a committed `tickets/**` path never rides the code lane."""

    code = "post_rebase_regate"

    def check(self, artifact: Candidate, workspace: Path) -> GateReport:
        findings = [
            Finding(code=self.code, path=p, message=f"the branch commits ticket-plane file {p}",
                    paved_road="leave outbox files uncommitted; the driver lifts them")
            for p in artifact.changed_files if p.startswith(f"{TICKETS_DIR}/")
        ]
        return GateReport(code=self.code, verdict="fail" if findings else "pass", findings=findings)


class ApprovalGate:
    """`correctness_review` participates as the pinned approval, never a re-executed call (section 9).

    The approval must name the pre-rebase head: it carries across a clean rebase, never across new commits.
    """

    code = "correctness_review"

    def check(self, artifact: Candidate, workspace: Path) -> GateReport:
        path = f"{TICKETS_DIR}/{artifact.stem}/review.md"
        road = f"re-run `run {artifact.stem}` so Review approves the current branch head"
        if artifact.review_text is None:
            return self._fail(path, "no review.md on main", road)
        try:
            review = read_review(artifact.review_text)
        except ValueError as e:
            return self._fail(path, f"review.md does not parse: {e}", road)
        if not isinstance(review, ApprovedInvoice):
            return self._fail(path, f"the pinned verdict is {review.verdict}, not approve", road)
        if review.reviewed_sha != artifact.reviewed_sha:
            return self._fail(path, f"the approval pins {review.reviewed_sha}, the branch head is"
                                    f" {artifact.reviewed_sha}", road)
        return GateReport(code=self.code, verdict="pass")

    def _fail(self, path: str, message: str, road: str) -> GateReport:
        return GateReport(code=self.code, verdict="fail",
                          findings=[Finding(code=self.code, path=path, message=message, paved_road=road)])


MERGE_GATES = (TicketSchemaGate(), PostRebaseGate(), ApprovalGate())


def squash_message(ticket: Ticket, reviewed_sha: str) -> str:
    """Subject `chupa(<stem>): <Goal line>` plus the trailers reconcile maps a commit back by (section 10)."""
    goal = next(line.strip() for line in ticket.sections["Goal / Why"].splitlines() if line.strip())
    return f"chupa({ticket.stem}): {goal}\n\nchupa-ticket: {ticket.stem}\nchupa-reviewed-sha: {reviewed_sha}\n"


def _refused(findings: list[Finding], cost: Cost) -> StageResult:
    return StageResult(outcome="gate_failed", artifact=None, findings=findings, cost=cost)


async def merge(ctx: StageContext, ticket: Ticket, *, attempt: int) -> StageResult:
    """Admit one reviewed branch to main, or refuse it with findings and main untouched."""
    stem = ticket.stem
    started = ctx.driver.clock()
    worktree = ctx.worktree(stem)
    reviewed = await ctx.git.rev_parse(ctx.repo, stem)

    # Lifted outbox copies show as tracked deletions in a worktree born from a main that already held
    # them, and a dirty tree refuses the rebase. Restoring to the branch's committed ticket plane (which
    # the branch never changes) makes the rebase land it on main's content; restoring main's content
    # BEFORE the rebase would itself dirty the index against the older branch head.
    await ctx.git.restore(worktree, [TICKETS_DIR], source=stem)
    try:
        await ctx.git.rebase(worktree, MAIN)
    except RebaseRefused as e:
        cost = Cost(seconds=(ctx.driver.clock() - started).total_seconds())
        return _refused([Finding(code="post_rebase_regate", message=f"rebase onto main refused: {e.err.strip()}",
                                 paved_road=f"re-run `run {stem}` so Implement re-branches from current main")],
                        cost)

    evidence = await gather_evidence(ctx, ticket, "ok", attempt=attempt, stage="merge")
    review_md = ctx.repo / TICKETS_DIR / stem / "review.md"
    candidate = Candidate(
        stem=stem, reviewed_sha=reviewed, changed_files=evidence.changed_files,
        ticket_text=(ctx.repo / ticket_path(stem)).read_text(),
        review_text=review_md.read_text() if review_md.is_file() else None,
    )
    severity = check_severity(ctx, ticket)
    gated = [run_gates(CHECK_GATES, evidence, worktree, severity=severity),
             run_gates(MERGE_GATES, candidate, ctx.repo, severity=severity)]
    if hard := [f for g in gated for r in g.hard_failures for f in r.findings]:
        return _refused(hard, Cost(seconds=(ctx.driver.clock() - started).total_seconds()))

    async def squash() -> dict:
        await ctx.git.merge_squash(ctx.repo, stem)
        await ctx.git.commit(ctx.repo, squash_message(ticket, reviewed))
        return {"commit": await ctx.git.rev_parse(ctx.repo, MAIN)}

    commit = (await ctx.driver.effects.run(squash, key="/".join(("merge", stem, str(attempt))), ticket=stem))["commit"]
    ctx.driver.journal.append(EventType.STATE_TRANSITION,
                              {"to": "merged", "commit": commit, "reviewed_sha": reviewed}, ticket=stem)
    await ctx.git.worktree_remove(ctx.repo, worktree)
    await ctx.git.branch_delete(ctx.repo, stem)
    admission = Admission(produced_by_spec_version=MERGE_SPEC_VERSION, produced_at_sha=commit,
                          stem=stem, commit=commit, reviewed_sha=reviewed)
    soft = [f for g in gated for f in g.findings]
    return StageResult(outcome="ok", artifact=admission, findings=soft,
                       cost=Cost(seconds=(ctx.driver.clock() - started).total_seconds()))
