"""The Implement, Check, and Review stages (CHUPA_PLAN.md sections 4, 5, 9, 10, 13; 19.P1).

Implement and Review are prompt specs run through the one driver; Check is mechanical. This module
owns stage-evidence gathering and the stage-terminal OUTBOX lift (section 9's ownership law): each
stage writes its artifact into `tickets/<stem>/` inside the worktree, and at the stage terminal the
lift moves it to the canonical tickets dir as ONE ticket-plane commit `chupa(<stem>): <kind>`.

The run's terminal `state_transition` is not written here: that is the runner's (section 11.2).
"""

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from chupa.artifacts import OUTCOMES, Artifact, Cost, Finding, NonBlank, Outcome, ReviewVerdict, StageResult
from chupa.config import Config, Severity
from chupa.driver import Driver, LlmStage
from chupa.gates import GateReport, run_gates
from chupa.git import Git, GitError
from chupa.journal import run_seq
from chupa.providers import child_env
from chupa.seams import ExecutableNotFound, FileSystem, ProcessExec
from chupa.specs import RenderOverBound, Spec, load_spec, render, resolve_plan_contract
from chupa.tickets import PLAN_FILE, TICKET_FILE, TICKETS_DIR, Ticket, ticket_path

MAIN = "main"
# Section 7 diff budget: sized so every rendered review prompt fits the serving provider's bound.
DIFF_BUDGET_FILES = 30
DIFF_BUDGET_INSERTED = 1_500
# The mechanical Check has no prompt spec; this versions its own contract in the provenance slot.
CHECK_SPEC_VERSION = 1
OUTPUT_TAIL_CHARS = 2_000
RUN_RECORD_SECTIONS = (
    "Outcome",
    "Surprises / judgment calls",
    "Dead ends",
    "Second problems filed",
    "Resolved engine/model",
    "Predicted vs actual",
)

StageName = Literal["implement", "check", "review"]


class _Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


# --- artifacts ----------------------------------------------------------------------------------


class ImplementReply(_Strict):
    """The implement surface's model-facing reply (specs/implement.md); the stage stamps provenance."""

    outcome: Literal["ok", "already_satisfied", "premise_failed"]
    summary: NonBlank
    surprises: str
    dead_ends: str
    predicted_vs_actual: str
    findings: list[Finding]

    @model_validator(mode="after")
    def _findings_match_outcome(self) -> "ImplementReply":
        if self.outcome == "premise_failed":
            if not self.findings or any(f.code != "premise" for f in self.findings):
                raise ValueError("premise_failed needs at least one finding, every code `premise`")
        elif self.findings:
            raise ValueError(f"{self.outcome} carries an empty findings list; reply premise_failed to stop")
        return self


class PackingSlip(Artifact):
    """Implement's artifact: the branch plus its run record (section 4)."""

    stem: NonBlank
    branch: NonBlank
    outcome: Literal["ok", "already_satisfied"]
    summary: NonBlank
    run_record: NonBlank  # repo-relative path of the lifted run.md


class Invoice(Artifact):
    """Check's artifact, persisted as `checks.json`: every mechanical gate report for one branch head."""

    stem: NonBlank
    passed: bool
    changed_files: list[str]
    inserted_lines: Annotated[int, Field(ge=0)]
    bypassed: list[str]  # gate codes the ticket's `gate_bypass` valve demoted to soft
    reports: list[GateReport]


class _Review(Artifact):
    stem: NonBlank
    reviewed_sha: NonBlank
    summary: NonBlank
    findings: list[Finding]
    spec_version: NonBlank
    provider: str | None
    model: str | None


class ApprovedInvoice(_Review):
    verdict: Literal["approve"]


class SnagList(_Review):
    verdict: Literal["snag"]


class Rma(_Review):
    verdict: Literal["rma"]


ReviewArtifact = Annotated[ApprovedInvoice | SnagList | Rma, Field(discriminator="verdict")]
EMITS_BY_VERDICT: Mapping[str, type[_Review]] = {"approve": ApprovedInvoice, "snag": SnagList, "rma": Rma}
_REVIEW = TypeAdapter(ReviewArtifact)
_REVIEW_JSON = re.compile(r"^```json\n(.*?)\n```$", re.DOTALL | re.MULTILINE)


def render_review(review: _Review) -> str:
    lines = [f"# Review: {review.verdict}", "", review.summary, "", "## Findings", ""]
    lines += [f"- [{f.code}] {f.path or '-'}:{f.line or '-'} {f.message} (do instead: {f.paved_road})"
              for f in review.findings] or ["none"]
    return "\n".join(lines + ["", "## Record", "", "```json", review.model_dump_json(indent=2), "```", ""])


def read_review(text: str) -> ApprovedInvoice | SnagList | Rma:
    """Parse `review.md`'s pinned record (the merge gate's on-disk input); the prose above it is not read."""
    m = _REVIEW_JSON.search(text)
    if m is None:
        raise ValueError("review.md carries no ```json record block; re-run Review to rewrite it")
    return _REVIEW.validate_json(m.group(1))


# --- context ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class StageContext:
    """The seams one ticket run's stages share. `env` is the parent env; children get it minus secrets."""

    repo: Path
    config: Config
    env: Mapping[str, str]
    exec_: ProcessExec
    git: Git
    fs: FileSystem
    driver: Driver
    specs_dir: Path

    def worktree(self, stem: str) -> Path:
        assert self.config.worktree_root is not None  # resolved at config load
        return self.config.worktree_root / stem


def _spec(ctx: StageContext, surface: str) -> Spec:
    return load_spec((ctx.specs_dir / f"{surface}.md").read_text())


def _major(spec: Spec) -> int:
    return int(spec.meta.version.split(".")[0])


def findings_text(findings: Sequence[Finding]) -> str:
    return "\n".join(f"- {f.code}: {f.message} (do instead: {f.paved_road})" for f in findings) or "none"


def _short(result: StageResult, outcome: Outcome, findings: list[Finding], artifact: Artifact | None = None) -> StageResult:
    return StageResult(outcome=outcome, artifact=artifact, findings=findings, cost=result.cost)


async def prepare_worktree(ctx: StageContext, stem: str) -> Path:
    """TEARDOWN-AND-CREATE (section 6): remove any worktree and branch a prior run left, then branch from main."""
    path = ctx.worktree(stem)
    if path.exists():
        await ctx.git.worktree_remove(ctx.repo, path)
    else:
        await ctx.git.worktree_prune(ctx.repo)
    try:
        await ctx.git.rev_parse(ctx.repo, f"refs/heads/{stem}")
    except GitError:
        pass  # no leftover branch
    else:
        await ctx.git.branch_delete(ctx.repo, stem)
    path.parent.mkdir(parents=True, exist_ok=True)
    await ctx.git.worktree_add(ctx.repo, path, stem, MAIN)
    return path


async def lift_outbox(ctx: StageContext, stem: str, kind: str, *, attempt: int) -> str | None:
    """Move the worktree outbox into the canonical ticket dir as ONE ticket-plane commit; None if empty.

    `ticket.md` is never lifted: it stays read-only to the agent (section 10). Keyed with the run
    sequence, so a same-run re-entry never commits twice.
    """
    outbox = ctx.worktree(stem) / TICKETS_DIR / stem
    files = sorted(p for p in outbox.rglob("*") if p.is_file() and p.relative_to(outbox) != Path(TICKET_FILE))
    if not files:
        return None

    async def commit() -> dict:
        rels = []
        for src in files:
            rel = f"{TICKETS_DIR}/{stem}/{src.relative_to(outbox).as_posix()}"
            ctx.fs.write(ctx.repo / rel, src.read_bytes())
            src.unlink()
            rels.append(rel)
        await ctx.git.add(ctx.repo, rels)
        await ctx.git.commit(ctx.repo, f"chupa({stem}): {kind}", only=rels)
        return {"kind": kind, "paths": rels, "commit": await ctx.git.rev_parse(ctx.repo, "HEAD")}

    key = "/".join(("ticket-plane", stem, str(attempt), kind))
    return (await ctx.driver.effects.run(commit, key=key, ticket=stem))["commit"]


# --- Implement ----------------------------------------------------------------------------------


def _context_text(ctx: StageContext, ticket: Ticket, worktree: Path) -> str:
    paths = list(dict.fromkeys([*ticket.context, *(str(p) for p in ctx.config.context_files)]))
    return "\n\n".join(f"### {p}\n{(worktree / p).read_text()}" for p in paths) or "none"


def implement_stage(ctx: StageContext, ticket: Ticket, worktree: Path) -> tuple[LlmStage, Spec]:
    spec = _spec(ctx, "implement")
    plan = (ctx.repo / PLAN_FILE).read_text() if ticket.plan_contract else ""
    inputs = {
        "ticket": (ctx.repo / ticket_path(ticket.stem)).read_text(),
        "plan_contract": resolve_plan_contract(plan, ticket.plan_contract) if ticket.plan_contract else "none",
        "context": _context_text(ctx, ticket, worktree),
    }

    def render_ticket(_: Ticket, findings: list[Finding]) -> str:
        return render(spec, {**inputs, "retry_findings": findings_text(findings)}, ticket.frontmatter.agent_effort)

    return LlmStage(surface="implement", emits=ImplementReply, gates=[], render=render_ticket), spec


def run_record(reply: ImplementReply, cost: Cost, spec: Spec) -> str:
    fields = {
        "Outcome": reply.outcome,
        "Surprises / judgment calls": reply.surprises,
        "Dead ends": reply.dead_ends,
        # The Suggestion Box ships with the Phase 2 spine; until then nothing files box messages.
        "Second problems filed": "none",
        "Resolved engine/model": f"- provider: {cost.provider}\n- model: {cost.model}\n"
                                 f"- spec: {spec.meta.llm_surface} {spec.meta.version}",
        "Predicted vs actual": reply.predicted_vs_actual,
    }
    return "".join(f"## {name}\n\n{(fields[name].strip() or 'none')}\n\n" for name in RUN_RECORD_SECTIONS)


async def implement(ctx: StageContext, ticket: Ticket, *, attempt: int) -> StageResult:
    """Teardown-and-create the worktree, run the implement spec in it, and write + lift the run record."""
    stem = ticket.stem
    worktree = await prepare_worktree(ctx, stem)
    stage, spec = implement_stage(ctx, ticket, worktree)
    try:
        result = await ctx.driver.run(
            stage, ticket, ticket=stem, attempt=attempt, workspace=worktree,
            tier=ticket.frontmatter.agent_tier, effort=ticket.frontmatter.agent_effort,
            stuck_budget=ticket.stuck_minutes * 60.0,
        )
    except RenderOverBound as e:
        # The pre-call short-circuit: ticket-text arithmetic, parked like premise_failed (section 8).
        return StageResult(outcome="premise_failed", artifact=None, findings=[e.finding], cost=Cost())
    if result.outcome != "ok":
        return result
    reply = result.artifact
    assert isinstance(reply, ImplementReply)
    record = f"{TICKETS_DIR}/{stem}/run.md"
    ctx.fs.write(worktree / record, run_record(reply, result.cost, spec).encode())
    await lift_outbox(ctx, stem, "run-record", attempt=attempt)
    if reply.outcome == "premise_failed":
        return _short(result, "premise_failed", list(reply.findings))
    slip = PackingSlip(
        produced_by_spec_version=_major(spec),
        produced_at_sha=await ctx.git.rev_parse(ctx.repo, stem),
        stem=stem, branch=stem, outcome=reply.outcome, summary=reply.summary, run_record=record,
    )
    return _short(result, "ok", [], slip)


# --- Check --------------------------------------------------------------------------------------


class CommandResult(_Strict):
    argv: list[str]
    rc: int | None  # None: the command could not run or timed out -- fails closed like a nonzero exit
    tail: str


class Evidence(_Strict):
    """Everything the mechanical gates judge, gathered once per branch head (the stage layer's job)."""

    stem: NonBlank
    head_sha: NonBlank
    claimed: Literal["ok", "already_satisfied"]
    scope_fence: list[str]
    changed_files: list[str]
    inserted_lines: int
    verification: list[CommandResult]
    run_record: str | None  # the lifted run.md text, None when absent


def _inserted(diff: str) -> int:
    return sum(line.startswith("+") and not line.startswith("+++") for line in diff.splitlines())


async def gather_evidence(
    ctx: StageContext, ticket: Ticket, claimed: Literal["ok", "already_satisfied"], *, attempt: int,
    stage: str = "check",
) -> Evidence:
    stem = ticket.stem
    worktree = ctx.worktree(stem)
    env = child_env(ctx.env, ctx.config)  # verification never inherits a provider key (section 6)
    results = []
    for n, argv in enumerate(ticket.verification, 1):
        try:
            rc, out, err = await ctx.exec_.run(list(argv), cwd=worktree, env=env, timeout=ticket.stuck_minutes * 60.0)
        except TimeoutError:
            rc, out, err = None, "", f"timed out after the ticket's stuck budget ({ticket.stuck_minutes}m)"
        except ExecutableNotFound as e:
            rc, out, err = None, "", str(e)
        ctx.driver.spool.write(stem, attempt, f"{stage}/verify-{n:02d}.txt",
                               f"$ {' '.join(argv)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
        tail = ctx.driver.redactor.scrub((out + err)[-OUTPUT_TAIL_CHARS:])
        results.append(CommandResult(argv=list(argv), rc=rc, tail=tail))
    run_md = ctx.repo / TICKETS_DIR / stem / "run.md"
    return Evidence(
        stem=stem,
        head_sha=await ctx.git.rev_parse(ctx.repo, stem),
        claimed=claimed,
        scope_fence=list(ticket.scope_fence),
        changed_files=await ctx.git.diff_names(ctx.repo, MAIN, stem),
        inserted_lines=_inserted(await ctx.git.diff(ctx.repo, MAIN, stem)),
        verification=results,
        run_record=run_md.read_text() if run_md.is_file() else None,
    )


def _report(code: str, findings: list[Finding]) -> GateReport:
    return GateReport(code=code, verdict="fail" if findings else "pass", findings=findings)


def _in_fence(path: str, prefixes: Sequence[str]) -> bool:
    return any(path == p or path.startswith(p if p.endswith("/") else p + "/") for p in prefixes)


class ScopeFenceGate:
    """The implement stage's write allowlist (section 9): the committed diff within `## Scope fence`.

    The stem's own outbox is exempt except `ticket.md`, which stays read-only to the agent (section 10).
    """

    code = "scope_fence"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        outbox = f"{TICKETS_DIR}/{artifact.stem}/"
        outside = [p for p in artifact.changed_files
                   if not _in_fence(p, artifact.scope_fence)
                   and not (p.startswith(outbox) and p != outbox + TICKET_FILE)]
        return _report(self.code, [
            Finding(code=self.code, path=p, message=f"{p} is outside `## Scope fence`",
                    paved_road="revert the edit and commit; if the criteria force it, reply premise_failed"
                               " naming the file so the fence is widened")
            for p in outside
        ])


class VerificationGate:
    """The ticket's own `## Verification` commands, all green on the branch (Phase 1: no base attribution).

    An EMPTY committed diff fails here unless Implement claimed `already_satisfied` (section 11).
    """

    code = "verification"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        findings = [
            Finding(code=self.code, message=f"`{' '.join(r.argv)}` exited {r.rc}: {r.tail.strip() or '(no output)'}",
                    paved_road=f"make `{' '.join(r.argv)}` exit 0 on the branch and commit the fix")
            for r in artifact.verification if r.rc != 0
        ]
        empty = not artifact.changed_files
        if empty and artifact.claimed == "ok":
            findings.append(Finding(code=self.code, message="the branch carries no committed change",
                                    paved_road="commit the work on the branch, or reply already_satisfied if every"
                                               " criterion already holds"))
        if not empty and artifact.claimed == "already_satisfied":
            findings.append(Finding(code=self.code, message="already_satisfied was claimed but the branch carries a"
                                    f" diff: {', '.join(artifact.changed_files)}",
                                    paved_road="reply ok for a branch with changes; already_satisfied commits nothing"))
        return _report(self.code, findings)


class RunRecordGate:
    """`run.md` present with the fixed section set and a closed-vocab `## Outcome` (section 13)."""

    code = "run_record"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        path = f"{TICKETS_DIR}/{artifact.stem}/run.md"
        road = "re-run Implement so the engine writes run.md with every section of section 13"
        if artifact.run_record is None:
            return _report(self.code, [Finding(code=self.code, path=path, message="run.md is missing",
                                               paved_road=road)])
        sections: dict[str, list[str]] = {}
        current = None
        for line in artifact.run_record.splitlines():
            if line.startswith("## "):
                current = line[3:].strip()
                sections[current] = []
            elif current is not None:
                sections[current].append(line)
        findings = []
        if tuple(sections) != RUN_RECORD_SECTIONS:
            findings.append(Finding(code=self.code, path=path, message=f"run.md sections are {list(sections)}",
                                    paved_road=f"use exactly {list(RUN_RECORD_SECTIONS)}, in order"))
        outcome = "\n".join(sections.get("Outcome", [])).strip()
        if outcome not in OUTCOMES:
            findings.append(Finding(code=self.code, path=path, message=f"`## Outcome` {outcome!r} is not an outcome",
                                    paved_road=f"use one of {sorted(OUTCOMES)}"))
        return _report(self.code, findings)


class DiffBudgetGate:
    """A mechanical cap on the reviewable diff, so the review prompt fits its bound (section 7)."""

    code = "diff_budget"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        files, inserted = len(artifact.changed_files), artifact.inserted_lines
        if files <= DIFF_BUDGET_FILES and inserted <= DIFF_BUDGET_INSERTED:
            return _report(self.code, [])
        return _report(self.code, [Finding(
            code=self.code,
            message=f"diff is {files} files / {inserted} inserted lines, over the budget of"
                    f" {DIFF_BUDGET_FILES} files / {DIFF_BUDGET_INSERTED} lines",
            paved_road="split the ticket into smaller stems, each under the diff budget",
        )])


CHECK_GATES: tuple[ScopeFenceGate | VerificationGate | RunRecordGate | DiffBudgetGate, ...] = (
    ScopeFenceGate(), VerificationGate(), RunRecordGate(), DiffBudgetGate(),
)


def check_severity(ctx: StageContext, ticket: Ticket) -> dict[str, Severity]:
    """Config severity with the ticket's `gate_bypass` valve applied: a bypassed code is soft for this ticket."""
    severity = dict(ctx.driver.severity)
    for bypass in ticket.frontmatter.gate_bypass:
        severity[bypass.code] = "soft"
    return severity


async def check(ctx: StageContext, ticket: Ticket, slip: PackingSlip, *, attempt: int) -> StageResult:
    """Invoicing: run the mechanical gates on the branch head, write + lift `checks.json`."""
    stem = ticket.stem
    started = ctx.driver.clock()
    evidence = await gather_evidence(ctx, ticket, slip.outcome, attempt=attempt)
    gated = run_gates(CHECK_GATES, evidence, ctx.worktree(stem), severity=check_severity(ctx, ticket))
    invoice = Invoice(
        produced_by_spec_version=CHECK_SPEC_VERSION, produced_at_sha=evidence.head_sha, stem=stem,
        passed=gated.passed, changed_files=evidence.changed_files, inserted_lines=evidence.inserted_lines,
        bypassed=sorted({b.code for b in ticket.frontmatter.gate_bypass}), reports=gated.reports,
    )
    ctx.fs.write(ctx.worktree(stem) / TICKETS_DIR / stem / "checks.json",
                 (invoice.model_dump_json(indent=2) + "\n").encode())
    await lift_outbox(ctx, stem, "checks", attempt=attempt)
    cost = Cost(seconds=(ctx.driver.clock() - started).total_seconds())
    if not gated.passed:
        hard = [f for r in gated.hard_failures for f in r.findings]
        return StageResult(outcome="gate_failed", artifact=invoice, findings=hard, cost=cost)
    outcome = "already_satisfied" if slip.outcome == "already_satisfied" else "ok"
    return StageResult(outcome=outcome, artifact=invoice, findings=gated.findings, cost=cost)


# --- Review -------------------------------------------------------------------------------------


def review_stage(ctx: StageContext, ticket_text: str, diff: str) -> tuple[LlmStage, Spec]:
    """specs/review.md wired UNCHANGED: the same spec and inputs the review baseline measured."""
    spec = _spec(ctx, "review")

    def render_diff(_: object, findings: list[Finding]) -> str:
        inputs = {"ticket": ticket_text, "diff": diff, "retry_findings": findings_text(findings)}
        return render(spec, inputs, spec.meta.effort)

    return LlmStage(surface="review", emits=ReviewVerdict, gates=[], render=render_diff), spec


async def review(ctx: StageContext, ticket: Ticket, invoice: Invoice, *, attempt: int) -> StageResult:
    """Inspect: one separate-session review of `git diff main...<stem>`, pinned to the reviewed SHA.

    approve -> ok; snag and rma -> gate_failed (the review surface is a gate, section 11); the
    verdict-keyed artifact lands in `review.md` either way.
    """
    stem = ticket.stem
    reviewed = await ctx.git.rev_parse(ctx.repo, stem)
    diff = await ctx.git.diff(ctx.repo, MAIN, stem)
    stage, spec = review_stage(ctx, (ctx.repo / ticket_path(stem)).read_text(), diff)
    try:
        # Tier is the ticket's (a surface invoked FOR a ticket, section 6); effort is the spec's, as baselined.
        result = await ctx.driver.run(
            stage, invoice, ticket=stem, attempt=attempt, workspace=ctx.worktree(stem),
            tier=ticket.frontmatter.agent_tier, effort=spec.meta.effort, stuck_budget=ticket.stuck_minutes * 60.0,
        )
    except RenderOverBound as e:
        return StageResult(outcome="premise_failed", artifact=None, findings=[e.finding], cost=Cost())
    if result.outcome != "ok":
        return result
    verdict = result.artifact
    assert isinstance(verdict, ReviewVerdict)
    artifact = EMITS_BY_VERDICT[verdict.verdict](
        produced_by_spec_version=_major(spec), produced_at_sha=reviewed, stem=stem, reviewed_sha=reviewed,
        verdict=verdict.verdict, summary=verdict.summary, findings=list(verdict.findings),
        spec_version=spec.meta.version, provider=result.cost.provider, model=result.cost.model,
    )
    ctx.fs.write(ctx.worktree(stem) / TICKETS_DIR / stem / "review.md", render_review(artifact).encode())
    await lift_outbox(ctx, stem, "review", attempt=attempt)
    if verdict.verdict == "approve":
        return _short(result, "ok", [], artifact)
    return _short(result, "gate_failed", list(verdict.findings), artifact)


# --- composition --------------------------------------------------------------------------------


@dataclass(frozen=True)
class StagesRun:
    """Every stage result of one run, in order; the run stops at the first stage not `ok`."""

    attempt: int
    results: dict[StageName, StageResult] = field(default_factory=dict)

    @property
    def last(self) -> tuple[StageName, StageResult]:
        return list(self.results.items())[-1]


async def run_stages(ctx: StageContext, ticket: Ticket) -> StagesRun:
    """Implement -> Check -> Review for one ticket, single worker, in the process holding the lock.

    `already_satisfied`, proven by Check's green verification on an empty diff, stops before Review:
    there is no diff to review and the ticket settles as a no-op (section 5 invariant 4).
    """
    run = StagesRun(attempt=run_seq(ctx.driver.journal.read(), ticket.stem))
    implemented = run.results["implement"] = await implement(ctx, ticket, attempt=run.attempt)
    if implemented.outcome != "ok":
        return run
    assert isinstance(implemented.artifact, PackingSlip)
    checked = run.results["check"] = await check(ctx, ticket, implemented.artifact, attempt=run.attempt)
    if checked.outcome != "ok":
        return run
    assert isinstance(checked.artifact, Invoice)
    run.results["review"] = await review(ctx, ticket, checked.artifact, attempt=run.attempt)
    return run
