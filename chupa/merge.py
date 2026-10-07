"""Merge: the single-admission writer to main (CHUPA_PLAN.md sections 7, 9, 10; 19.P1).

Per admission, all before main moves: restore the worktree's ticket plane -> rebase onto main ->
re-run the mechanical hard set on the rebased candidate -> require the pinned review approval ->
squash-merge with trailers -> journal `to: merged` -> delete the worktree and branch. Runs inline
in the one CLI process holding the single-writer lock; the serial merge task, red-streak pause, and
tree-hash assert are Phase 3. The bug gate is deferred to its first bug-intake consumer (Phase 6).

A refusal leaves main untouched and the branch in place; journaling a non-ok terminal is the
runner's (section 11.2).
"""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chupa.daemon import PauseConsumer

from pydantic import BaseModel, ConfigDict, ValidationError

from chupa.artifacts import Artifact, Cost, Finding, NonBlank, StageResult
from chupa.gates import GateReport, run_gates
from chupa.git import GitError, RebaseRefused
from chupa.journal import Event, EventType
from chupa.stages import (
    CHECK_GATES,
    MAIN,
    ApprovedInvoice,
    Invoice,
    StageContext,
    check_severity,
    gather_evidence,
    read_review,
)
from chupa.tickets import TICKETS_DIR, Ticket, TicketInvalid, ticket_path, validate_ticket

# Versions the merge contract in the provenance slot, like the mechanical Check.
MERGE_SPEC_VERSION = 1


def compose_pipeline(ctx: StageContext, *, escalate: Callable[[Event], None],
                     control: "PauseConsumer | None") -> "MergeQueue":
    """Compose admission without running it; bootstrap dispatch still merges inline."""
    # The queue's priority helpers import drain, which imports runner and this module.
    from chupa.mergequeue import MergeQueue

    from chupa.runner import Refusal

    if control is None:
        raise Refusal("admission control consumer absent",
                      "construct it with `build_control` at the composition root and supply it as `Checkout.control`")
    return MergeQueue(ctx, escalate=escalate, control=control)


class Candidate(BaseModel):
    """What the merge-only gates judge: the rebased branch plus main's ticket and pinned review."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    stem: NonBlank
    reviewed_sha: NonBlank  # the branch head Review saw, before the rebase
    changed_files: list[str]
    ticket_text: str
    review_text: str | None  # main's `review.md`, None when absent
    seeds: list["SeedOnMain"] = []
    seed_checks_text: str | None = None


class SeedOnMain(BaseModel):
    """A journaled seed's blob as committed on main before the admission rebase."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    stem: NonBlank
    ticket_sha: str | None
    ticket_text: str | None


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


class SeedSafetyGate:
    """MERGE-SAFETY: every journaled seed still has an approval for main's exact committed blob."""

    code = "requisition_review"

    def check(self, artifact: Candidate, workspace: Path) -> GateReport:
        if not artifact.seeds:
            return GateReport(code=self.code, verdict="pass")
        path = f"{TICKETS_DIR}/{artifact.stem}/checks.json"
        road = f"re-run `run {artifact.stem}` so Check records approvals for the committed seeds"
        findings = []
        if artifact.seed_checks_text is None:
            findings.append(Finding(code=self.code, path=path, message="checks.json is missing on main",
                                    paved_road=road))
            reviews = []
        else:
            try:
                reviews = Invoice.model_validate_json(artifact.seed_checks_text).seeds
            except ValidationError as exc:
                findings.append(Finding(code=self.code, path=path,
                                        message=f"checks.json does not parse: {exc.error_count()} schema error(s)",
                                        paved_road=road))
                reviews = []
        for seed in artifact.seeds:
            seed_path = ticket_path(seed.stem)
            if seed.ticket_sha is None or seed.ticket_text is None:
                findings.append(Finding(code=self.code, path=seed_path, message="seed is missing on main",
                                        paved_road=road))
                continue
            if not any(r.stem == seed.stem and r.verdict == "approve" and r.ticket_sha == seed.ticket_sha
                       for r in reviews):
                findings.append(Finding(code=self.code, path=seed_path,
                                        message="no approve verdict pins the committed seed ticket.md blob",
                                        paved_road=road))
            try:
                validate_ticket(seed.stem, seed.ticket_text, workspace)
            except TicketInvalid as exc:
                findings.extend(f.model_copy(update={"code": self.code}) for f in exc.findings)
        return GateReport(code=self.code, verdict="fail" if findings else "pass", findings=findings)


MERGE_GATES = (TicketSchemaGate(), PostRebaseGate(), ApprovalGate(), SeedSafetyGate())


def squash_message(ticket: Ticket, reviewed_sha: str) -> str:
    """Subject `chupa(<stem>): <Goal line>` plus the trailers reconcile maps a commit back by (section 10)."""
    goal = next(line.strip() for line in ticket.sections["Goal / Why"].splitlines() if line.strip())
    return f"chupa({ticket.stem}): {goal}\n\nchupa-ticket: {ticket.stem}\nchupa-reviewed-sha: {reviewed_sha}\n"


def _refused(findings: list[Finding], cost: Cost) -> StageResult:
    return StageResult(outcome="gate_failed", artifact=None, findings=findings, cost=cost)


async def gather_seeds(ctx: StageContext, ticket: Ticket) -> tuple[list[SeedOnMain], str | None]:
    """Pin seed approval custody to main's committed blobs before the admission rebase."""
    stem = ticket.stem
    seeded_stems = sorted({e.ticket for e in ctx.driver.journal.read()
                           if e.type == EventType.SIGNAL and e.ticket is not None
                           and e.body.get("signal") == "ticket_intake" and e.body.get("seeded_by") == stem})
    seeds = []
    for seed_stem in seeded_stems:
        path = ticket_path(seed_stem)
        try:
            sha = await ctx.git.rev_parse(ctx.repo, f"{MAIN}:{path}")
            text = await ctx.git._run(ctx.repo, "show", f"{MAIN}:{path}")
        except GitError:
            sha, text = None, None
        seeds.append(SeedOnMain(stem=seed_stem, ticket_sha=sha, ticket_text=text))
    checks_text = None
    if seeds:
        try:
            checks_text = await ctx.git._run(ctx.repo, "show", f"{MAIN}:{TICKETS_DIR}/{stem}/checks.json")
        except GitError:
            pass

    return seeds, checks_text


def read_candidate(ctx: StageContext, ticket: Ticket, reviewed: str, changed_files: list[str],
                   seeds: list[SeedOnMain], checks_text: str | None) -> Candidate:
    stem = ticket.stem
    review_md = ctx.repo / TICKETS_DIR / stem / "review.md"
    return Candidate(
        stem=stem, reviewed_sha=reviewed, changed_files=changed_files,
        ticket_text=(ctx.repo / ticket_path(stem)).read_text(),
        review_text=review_md.read_text() if review_md.is_file() else None,
        seeds=seeds, seed_checks_text=checks_text,
    )


async def merge(ctx: StageContext, ticket: Ticket, *, attempt: int) -> StageResult:
    """Admit one reviewed branch to main, or refuse it with findings and main untouched."""
    stem = ticket.stem
    started = ctx.driver.clock()
    worktree = ctx.worktree(stem)
    reviewed = await ctx.git.rev_parse(ctx.repo, stem)
    seeds, checks_text = await gather_seeds(ctx, ticket)

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
    candidate = read_candidate(ctx, ticket, reviewed, evidence.changed_files, seeds, checks_text)
    severity = check_severity(ctx, ticket)
    if candidate.seeds:
        severity["requisition_review"] = "hard"  # a seeded branch needs an exact committed approval
    gated = [run_gates(CHECK_GATES, evidence, worktree, severity=severity),
             run_gates(MERGE_GATES, candidate, ctx.repo, severity=severity)]
    if hard := [f for g in gated for r in g.hard_failures for f in r.findings]:
        return _refused(hard, Cost(seconds=(ctx.driver.clock() - started).total_seconds()))

    admission = await write_squash(ctx, ticket, reviewed, attempt=attempt)
    await retire(ctx, stem)
    soft = [f for g in gated for f in g.findings]
    return StageResult(outcome="ok", artifact=admission, findings=soft,
                       cost=Cost(seconds=(ctx.driver.clock() - started).total_seconds()))


async def write_squash(ctx: StageContext, ticket: Ticket, reviewed: str, *, attempt: int) -> Admission:
    """The shared code-lane Effect and merged-terminal writer; retirement follows tree validation."""
    stem = ticket.stem

    async def squash() -> dict:
        await ctx.git.merge_squash(ctx.repo, stem)
        await ctx.git.commit(ctx.repo, squash_message(ticket, reviewed))
        return {"commit": await ctx.git.rev_parse(ctx.repo, MAIN)}

    commit = (await ctx.driver.effects.run(squash, key="/".join(("merge", stem, str(attempt))), ticket=stem))["commit"]
    ctx.driver.journal.append(EventType.STATE_TRANSITION,
                              {"to": "merged", "commit": commit, "reviewed_sha": reviewed}, ticket=stem)
    return Admission(produced_by_spec_version=MERGE_SPEC_VERSION, produced_at_sha=commit,
                     stem=stem, commit=commit, reviewed_sha=reviewed)


async def retire(ctx: StageContext, stem: str) -> None:
    await ctx.git.worktree_remove(ctx.repo, ctx.worktree(stem))
    await ctx.git.branch_delete(ctx.repo, stem)
