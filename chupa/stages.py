"""The Implement, Check, and Review stages (CHUPA_PLAN.md sections 4, 5, 9, 10, 13; 19.P1).

Implement and Review are prompt specs run through the one driver; Check is mechanical. This module
owns stage-evidence gathering and the stage-terminal OUTBOX lift (section 9's ownership law): each
stage writes its artifact into `tickets/<stem>/` inside the worktree, and at the stage terminal the
lift moves it to the canonical tickets dir as ONE ticket-plane commit `chupa(<stem>): <kind>`.

The run's terminal `state_transition` is not written here: that is the runner's (section 11.2).
"""

import asyncio
import difflib
import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from chupa.artifacts import RELIABILITY_BATTERY_REPORT, ReliabilityBatteryReport, DAEMON_SOAK_REPORT, OUTCOMES, SHAKEOUT_REPORT, Artifact, Cost, DaemonSoakReport, Diagnosis, DiagnosisReply, Finding, Harvest, NonBlank, Outcome, ReviewVerdict, ShakeoutReport, StageResult
from chupa.box import BOX_DIR
from chupa.storm import arrival_id
from chupa.caps import lineage
from chupa.config import Config, ConfigSnapshot, Severity
from chupa.driver import Driver, LlmStage
from chupa.gates import GateReport, run_gates
from chupa.git import Git, GitError
from chupa.journal import TERMINAL_STATES, EventType, run_seq
from chupa.providers import child_env
from chupa.seams import ExecutableNotFound, FileSystem, ProcessExec
from chupa.specs import PlanContractError, RenderOverBound, Spec, entry_unit_gap, hardenable_units, load_spec, plan_id, render, required_units, resolve_plan_contract, without_unit
from chupa.tickets import _HEADING, _bullets, _sections, PLAN_FILE, TICKET_FILE, TICKETS_DIR, Ticket, TicketInvalid, ticket_path, validate_ticket

MAIN = "main"
KNOWN_ARTIFACTS: Mapping[str, type[BaseModel]] = {SHAKEOUT_REPORT: ShakeoutReport,
                                             DAEMON_SOAK_REPORT: DaemonSoakReport,
                                             RELIABILITY_BATTERY_REPORT: ReliabilityBatteryReport}
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
# Section 11.2: the attempt-scoped re-entry block's heading, rendered in criteria-position.
PRIOR_ATTEMPTS = "## Prior attempts (attempt-scoped, informational, unverified, not reviewed)"
DIAGNOSIS_STUCK_S = 600.0


class _Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


# --- artifacts ----------------------------------------------------------------------------------


class SecondProblem(_Strict):
    summary: NonBlank


class ImplementReply(_Strict):
    """The implement surface's model-facing reply (specs/implement.md); the stage stamps provenance."""

    outcome: Literal["ok", "already_satisfied", "premise_failed"]
    summary: NonBlank
    surprises: str
    dead_ends: str
    predicted_vs_actual: str
    findings: list[Finding]
    second_problems: list[SecondProblem] = []

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


class SeedReview(_Strict):
    """The Check verdict for one authored seed, pinned to its ticket.md blob."""

    stem: NonBlank
    ticket_sha: NonBlank
    verdict: Literal["approve", "snag", "rma"]
    findings: list[Finding]
    mechanical: str | None


class Invoice(Artifact):
    """Check's artifact, persisted as `checks.json`: every mechanical gate report for one branch head."""

    stem: NonBlank
    passed: bool
    changed_files: list[str]
    inserted_lines: Annotated[int, Field(ge=0)]
    bypassed: list[str]  # gate codes the ticket's `gate_bypass` valve demoted to soft
    reports: list[GateReport]
    seeds: list[SeedReview] = []
    verification: list["CommandResult"] = []


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


@dataclass
class StageBoundary:
    """Memory-only selection supplied by the lifetime; bootstrap has no suspension policy."""

    select: Callable[[Ticket, StageName], bool] | None = None
    run: "StagesRun | None" = None
    ticket: Ticket | None = None
    next_stage: StageName | None = None
    active: asyncio.Task | None = None


@dataclass(frozen=True)
class StageContext:
    """The seams one ticket run's stages share. `env` is the parent env; children get it minus secrets."""

    repo: Path
    config: Config | ConfigSnapshot
    env: Mapping[str, str]
    exec_: ProcessExec
    git: Git
    fs: FileSystem
    driver: Driver
    specs_dir: Path
    boundary: StageBoundary = field(default_factory=StageBoundary, init=False, compare=False)

    def worktree(self, stem: str) -> Path:
        assert self.config.worktree_root is not None  # resolved at config load
        return self.config.worktree_root / stem

    async def abort_current(self) -> None:
        from chupa.daemon import _protected_cleanup

        try:
            await self.driver.abort_current()
        finally:
            task = self.boundary.active
            if task is not None:
                if not task.done() and not task.cancelling():
                    task.cancel()
                cleanup = asyncio.gather(task, return_exceptions=True)
                await _protected_cleanup(cleanup)
                [result] = cleanup.result()
                if isinstance(result, BaseException) and not isinstance(result, asyncio.CancelledError):
                    raise result


class ArtifactInvalid(Exception):
    def __init__(self, path: Path, error: Exception) -> None:
        super().__init__(f"{path}: {error}")
        self.path = path
        self.error = error


def _registered_files(outbox: Path) -> list[Path]:
    return [p for p in outbox.rglob("*") if p.is_file() and p.name in KNOWN_ARTIFACTS]


def _lift_files(ctx: StageContext, stem: str, kind: str, only: str | None = None) -> list[Path]:
    outbox = ctx.worktree(stem) / TICKETS_DIR / stem
    canonical = ctx.repo / TICKETS_DIR / stem
    return sorted(p for p in outbox.rglob("*") if p.is_file()
                  and p.relative_to(outbox) != Path(TICKET_FILE)
                  and (only is None or p.relative_to(outbox).as_posix() == only)
                  and (p.name not in KNOWN_ARTIFACTS or kind == "checks")
                  and not ((c := canonical / p.relative_to(outbox)).is_file()
                           and c.read_bytes() == p.read_bytes()))


def _validate_reports(paths: Sequence[Path]) -> None:
    for path in paths:
        if path.name in KNOWN_ARTIFACTS:
            try:
                KNOWN_ARTIFACTS[path.name].model_validate_json(path.read_bytes())
            except Exception as error:
                raise ArtifactInvalid(path, error) from error


async def dirty_code(ctx: StageContext, stem: str) -> list[str]:
    # NUL records preserve filenames and include both sides of a staged rename.
    records = iter((await ctx.git._run(ctx.worktree(stem), "status", "--porcelain",
                                      "--untracked-files=all", "-z")).rstrip("\0").split("\0"))
    paths = []
    for record in records:
        if not record:
            continue
        paths.append(record[3:])
        if "R" in record[:2] or "C" in record[:2]:
            paths.append(next(records))
    outbox = f"{TICKETS_DIR}/{stem}/"
    return [p for p in paths if not p.startswith(outbox) or p == outbox + TICKET_FILE]


def _spec(ctx: StageContext, surface: str) -> Spec:
    return load_spec((ctx.specs_dir / f"{surface}.md").read_text())


def _major(spec: Spec) -> int:
    return int(spec.meta.version.split(".")[0])


def findings_text(findings: Sequence[Finding]) -> str:
    return "\n".join(f"- {f.code}: {f.message} (do instead: {f.paved_road})" for f in findings) or "none"


@dataclass(frozen=True)
class DiagnosisMaterial:
    ticket: str
    terminal: str
    stage: str | None
    harvest: Harvest | None
    run_record: str | None


def diagnose_stage(spec: Spec, material: DiagnosisMaterial) -> LlmStage:
    """The one pure diagnosis render, shared with the real-model evaluation."""
    inputs = {
        "ticket": material.ticket,
        "terminal": f"{material.terminal} at {material.stage or 'none'}",
        "harvest": material.harvest.model_dump_json() if material.harvest else "none",
        "run_record": material.run_record or "none",
    }

    def render_material(_: DiagnosisMaterial, findings: list[Finding]) -> str:
        return render(spec, {**inputs, "retry_findings": findings_text(findings)})

    return LlmStage(surface="diagnose", emits=DiagnosisReply, gates=[], render=render_material)


async def write_diagnosis(ctx: StageContext, ticket: Ticket, *, attempt: int, terminal: str,
                          stage: str | None, verdict: str, lessons: list[str],
                          mechanical: str | None, cost: Cost = Cost()) -> Diagnosis:
    spec = _spec(ctx, "diagnose")
    record = Diagnosis(
        produced_by_spec_version=_major(spec), produced_at_sha=await ctx.git.rev_parse(ctx.repo, ticket.stem),
        stem=ticket.stem, attempt=attempt, terminal=terminal, stage=stage, verdict=verdict,
        lessons=lessons, mechanical=mechanical, spec_version=spec.meta.version,
        provider=cost.provider, model=cost.model,
    )
    ctx.fs.write(ctx.worktree(ticket.stem) / TICKETS_DIR / ticket.stem / "diagnosis.json",
                 (record.model_dump_json(indent=2) + "\n").encode())
    await lift_outbox(ctx, ticket.stem, "diagnosis", attempt=attempt, only="diagnosis.json")
    return record


async def diagnose(ctx: StageContext, ticket: Ticket, material: DiagnosisMaterial, *, attempt: int) -> Diagnosis:
    spec = _spec(ctx, "diagnose")
    result = await ctx.driver.run(
        diagnose_stage(spec, material), material, ticket=ticket.stem, attempt=attempt,
        workspace=ctx.worktree(ticket.stem), tier=ticket.frontmatter.agent_tier,
        effort=ticket.frontmatter.agent_effort, stuck_budget=DIAGNOSIS_STUCK_S,
        expected_budget=ticket.expected_minutes * 60.0, scope_fence=())
    reply = result.artifact
    if result.outcome == "ok" and isinstance(reply, DiagnosisReply):
        return await write_diagnosis(ctx, ticket, attempt=attempt, terminal=material.terminal,
                                     stage=material.stage, verdict=reply.verdict, lessons=list(reply.lessons),
                                     mechanical=None, cost=result.cost)
    return await write_diagnosis(ctx, ticket, attempt=attempt, terminal=material.terminal,
                                 stage=material.stage, verdict="abandon-human", lessons=[],
                                 mechanical=f"no schema-valid verdict ({result.outcome})", cost=result.cost)


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


async def lift_outbox(ctx: StageContext, stem: str, kind: str, *, attempt: int,
                      only: str | None = None) -> str | None:
    """Move the worktree outbox into the canonical ticket dir as ONE ticket-plane commit; None if empty.

    `ticket.md` is never lifted: it stays read-only to the agent (section 10). Keyed with the run
    sequence, so a same-run re-entry never commits twice. A file byte-equal to its canonical copy is a prior
    run's artifact the worktree inherited from main, not this stage's output: it is never lifted.
    """
    outbox = ctx.worktree(stem) / TICKETS_DIR / stem
    files = _lift_files(ctx, stem, kind, only)
    if not files:
        return None
    _validate_reports(files)

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


def implement_inputs(repo: Path, plan: str, ticket_text: str, ticket: Ticket,
                     context_files: Sequence[Path]) -> dict[str, str]:
    """The production Implement inputs, also used to measure a ticket at authoring."""
    paths = list(dict.fromkeys([*ticket.context, *(str(p) for p in context_files)]))
    context = "\n\n".join(f"### {p}\n{(repo / p).read_text()}" for p in paths) or "none"
    return {
        "ticket": ticket_text,
        "plan_contract": resolve_plan_contract(plan, ticket.plan_contract) if ticket.plan_contract else "none",
        "context": context,
    }


def _one_line(text: str) -> str:
    # A payload newline could forge a ticket section heading inside the rendered ticket block.
    return " ".join(text.split())


def _prior_findings(ctx: StageContext, stem: str, stage: str | None) -> list[Finding]:
    """The terminal stage's durable findings artifact in the canonical ticket dir; [] when it wrote none."""
    root = ctx.repo / TICKETS_DIR / stem
    if stage == "review" and (path := root / "review.md").is_file():
        return list(read_review(path.read_text()).findings)
    if stage == "check" and (path := root / "checks.json").is_file():
        invoice = Invoice.model_validate_json(path.read_text())
        return [f for r in invoice.reports if r.verdict == "fail" for f in r.findings]
    return []


def _quoted(text: str) -> str:
    return "\n".join(f"> {line}" for line in text.split("\n"))


def prior_attempts(ctx: StageContext, stem: str) -> str | None:
    """Section 11.2 re-entry: the prior terminal and its findings as a clear-these block; None on a first attempt.

    Folded fresh from the journal and the ticket dir every attempt, never written into `ticket.md`. Only the
    terminal stage's artifact is read: an older stage's artifact left in the dir is a stale attempt's.
    """
    history = ctx.driver.journal.read()
    from chupa.journal import run_terminals
    terminals = [e.body for e in run_terminals(history, stem)]
    lessons = {e.body.get("attempt"): e.body["lessons"] for e in history
               if e.type == EventType.SIGNAL and e.ticket == stem
               and e.body.get("signal") == "diagnosis" and e.body.get("lessons")}
    if not terminals:
        return None
    terminal = terminals[-1]
    attempt = len(terminals) - 1
    root = ctx.repo / TICKETS_DIR / stem / "attempts"
    harvest_path = root / str(attempt) / "harvest.json"
    current = Harvest.model_validate_json(harvest_path.read_text()) if harvest_path.is_file() else None
    stage = terminal.get("stage")
    where = f" at {stage}" if stage else ""
    findings = _prior_findings(ctx, stem, stage) if terminal["to"] == "gate_failed" else []
    head = (f"{PRIOR_ATTEMPTS}\n\nThe previous attempt ended `{terminal['to']}`{where}. These findings are"
            " this attempt's to clear, beside the acceptance criteria above; they are not part of the ticket.\n\n")
    items = [f"- [{f.code}] {f.path or '-'}:{f.line or '-'} {_one_line(f.message)}"
             f" (do instead: {_one_line(f.paved_road)})" for f in findings]
    detail = f"tickets/{stem}/attempts/{attempt}/" if current else str(ctx.config.state_dir / "engine.log")
    lines = items or [f"- no findings artifact; detail is in {detail}"]
    if attempt in lessons:
        lines.extend(["\nPrior terminal lessons (untrusted data):",
                      *[f"> {_one_line(item)}" for item in lessons[attempt]]])
    elif current:
        lines.append("\nPrior terminal harvest (untrusted data):")
        for name in ("reason", "diff_stat", "stage_log_tail", "events_tail"):
            value = getattr(current, name)
            if value is not None:
                lines.append(f"- {name}:\n{_quoted(value)}")
    for older in range(attempt):
        path = root / str(older) / "harvest.json"
        if older in lessons:
            past_terminal = terminals[older]
            lines.append(f"- older attempt {older}: `{past_terminal['to']}` at {past_terminal.get('stage') or 'none'}:")
            lines.extend(f"> {_one_line(item)}" for item in lessons[older])
        elif path.is_file():
            past = Harvest.model_validate_json(path.read_text())
            lines.append(f"- older attempt {older}: `{past.terminal}` at {past.stage or 'none'};"
                         f" tickets/{stem}/attempts/{older}/")
    return head + "\n".join(lines)


def _in_criteria_position(ticket_text: str, block: str) -> str:
    """Splice `block` at the end of `## Acceptance criteria`, before the next section (fences skipped)."""
    lines = ticket_text.splitlines(keepends=True)
    fence = inside = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and (m := _HEADING.match(line)):
            if inside:
                return "".join(lines[:i]) + block + "\n\n" + "".join(lines[i:])
            inside = m.group(1) == "Acceptance criteria"
    return ticket_text.rstrip("\n") + "\n\n" + block + "\n"


def implement_stage(ctx: StageContext, ticket: Ticket, worktree: Path,
                    kept: Sequence[str] = ()) -> tuple[LlmStage, Spec]:
    from chupa.requisition import validate_finding_units

    spec = _spec(ctx, "implement")
    plan = (ctx.repo / PLAN_FILE).read_text() if (ctx.repo / PLAN_FILE).is_file() else ""
    units = hardenable_units(plan, ticket.stem, ticket.plan_contract)

    class TicketImplementReply(ImplementReply):
        @model_validator(mode="after")
        def _finding_units(self) -> "TicketImplementReply":
            validate_finding_units(self.findings, units)
            return self

    ticket_text = (ctx.repo / ticket_path(ticket.stem)).read_text()
    if (prior := prior_attempts(ctx, ticket.stem)) is not None:
        ticket_text = _in_criteria_position(ticket_text, prior)
    if kept:
        ticket_text = _in_criteria_position(ticket_text, (
            f"{APPROVED_SEEDS}\n\nThese seeds passed requisition_review and are already in your worktree."
            " Leave each one byte-identical and author only the rest:\n" + "\n".join(f"- {p}" for p in kept)))
    inputs = implement_inputs(worktree, plan, ticket_text, ticket, ctx.config.context_files)

    def render_ticket(_: Ticket, findings: list[Finding]) -> str:
        return render(spec, {**inputs, "retry_findings": findings_text(findings)})

    return LlmStage(surface="implement", emits=TicketImplementReply, gates=[], render=render_ticket), spec


def run_record(reply: ImplementReply | None, cost: Cost, spec: Spec, second_problem_ids: Sequence[str],
               *, outcome: Outcome | None = None) -> str:
    fields = {
        "Outcome": outcome or reply.outcome,
        "Surprises / judgment calls": reply.surprises if reply else 'none',
        "Dead ends": reply.dead_ends if reply else 'none',
        "Second problems filed": "\n".join(
            f"- {id}: {_one_line(problem.summary)}"
            for id, problem in zip(second_problem_ids, reply.second_problems if reply else (), strict=True)
        ) or "none",
        "Resolved engine/model": f"- provider: {cost.provider}\n- model: {cost.model}\n"
                                 f"- spec: {spec.meta.llm_surface} {spec.meta.version}",
        "Predicted vs actual": reply.predicted_vs_actual if reply else 'none',
    }
    return "".join(f"## {name}\n\n{(fields[name].strip() or 'none')}\n\n" for name in RUN_RECORD_SECTIONS)


async def implement(ctx: StageContext, ticket: Ticket, *, attempt: int) -> StageResult:
    """Teardown-and-create the worktree, run the implement spec in it, and write + lift the run record."""
    stem = ticket.stem
    worktree = await prepare_worktree(ctx, stem)
    kept = _restore_approved_seeds(ctx, stem, worktree) if TICKETS_DIR in ticket.scope_fence else []
    stage, spec = implement_stage(ctx, ticket, worktree, kept)
    try:
        result = await ctx.driver.run(
            stage, ticket, ticket=stem, attempt=attempt, workspace=worktree,
            tier=ticket.frontmatter.agent_tier, effort=ticket.frontmatter.agent_effort,
            stuck_budget=ticket.stuck_minutes * 60.0,
            expected_budget=ticket.expected_minutes * 60.0, scope_fence=ticket.scope_fence)
    except RenderOverBound as e:
        # The pre-call short-circuit: ticket-text arithmetic, parked like premise_failed (section 8).
        return StageResult(outcome="premise_failed", artifact=None, findings=[e.finding], cost=Cost())
    if result.outcome != "ok":
        if result.cost.provider is not None:
            record = f'{TICKETS_DIR}/{stem}/run.md'
            ctx.fs.write(worktree / record, run_record(None, result.cost, spec, [], outcome=result.outcome).encode())
            await lift_outbox(ctx, stem, 'run-record', attempt=attempt)
        return result
    reply = result.artifact
    assert isinstance(reply, ImplementReply)
    from chupa.daemon import storm_producer

    box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs,
                         journal=ctx.driver.journal, clock=ctx.driver.clock)
    second_problem_ids = [
        box.enqueue(message_class="suggestion", origin=stem, stage="implement",
                    outcome=reply.outcome, summary=problem.summary,
                    occurrence_id=arrival_id("second-problem", stem, attempt, index))[0]
        for index, problem in enumerate(reply.second_problems)
    ]
    record = f"{TICKETS_DIR}/{stem}/run.md"
    ctx.fs.write(worktree / record, run_record(reply, result.cost, spec, second_problem_ids).encode())
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
    base_red: bool = False


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
    # Main's and the branch's plan, gathered only when a `CHUPA_PLAN.md#<unit>` fence entry may admit a plan edit.
    plan_main: str | None = None
    plan_head: str | None = None
    report_paths: list[str] = []
    report_findings: list[Finding] = []


def _inserted(diff: str) -> int:
    return sum(line.startswith("+") and not line.startswith("+++") for line in diff.splitlines())


async def gather_evidence(
    ctx: StageContext, ticket: Ticket, claimed: Literal["ok", "already_satisfied"], *, attempt: int,
    stage: str = "check",
) -> Evidence:
    stem = ticket.stem
    worktree = ctx.worktree(stem)
    outbox = worktree / TICKETS_DIR / stem
    for path in _registered_files(outbox):
        path.unlink()
    env = child_env(ctx.env, ctx.config)  # verification never inherits a provider key (section 6)
    results = []
    red: list[tuple[int, list[str]]] = []
    timeout = ticket.stuck_minutes * 60.0
    for n, argv in enumerate(ticket.verification, 1):
        try:
            rc, out, err = await ctx.exec_.run(list(argv), cwd=worktree, env=env, timeout=timeout)
        except TimeoutError:
            rc, out, err = None, "", f"timed out after the ticket's stuck budget ({ticket.stuck_minutes}m)"
        except ExecutableNotFound as e:
            rc, out, err = None, "", str(e)
        ctx.driver.spool.write(stem, attempt, f"{stage}/verify-{n:02d}.txt",
                               f"$ {' '.join(argv)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
        tail = ctx.driver.redactor.scrub((out + err)[-OUTPUT_TAIL_CHARS:])
        results.append(CommandResult(argv=list(argv), rc=rc, tail=tail))
        if rc != 0:
            red.append((n, list(argv)))
    if red:
        base = await ctx.git.merge_base(ctx.repo, MAIN, stem)
        assert ctx.config.worktree_root is not None
        base_worktree = ctx.config.worktree_root / ".base" / stem
        if base_worktree.exists():
            await ctx.git.worktree_remove(ctx.repo, base_worktree)
        base_worktree.parent.mkdir(parents=True, exist_ok=True)
        await ctx.git.worktree_add_detached(ctx.repo, base_worktree, base)
        try:
            from chupa.daemon import storm_producer

            box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs,
                                 journal=ctx.driver.journal, clock=ctx.driver.clock)
            for n, argv in red:
                try:
                    rc, out, err = await ctx.exec_.run(argv, cwd=base_worktree, env=env, timeout=timeout)
                except TimeoutError:
                    rc, out, err = None, "", f"timed out after the ticket's stuck budget ({ticket.stuck_minutes}m)"
                except ExecutableNotFound as e:
                    rc, out, err = None, "", str(e)
                ctx.driver.spool.write(stem, attempt, f"{stage}/verify-{n:02d}-base.txt",
                                       f"$ {' '.join(argv)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
                if rc != 0:
                    results[n - 1] = results[n - 1].model_copy(update={"base_red": True})
                    summary = (f"`{' '.join(argv)}` fails on the merge base {base[:8]} too;"
                               " fix main, not this ticket")
                    if not any(m.message_class == "failure_report" and m.origin == stem
                               and m.outcome == "base_red"
                               and m.summary.startswith(f"`{' '.join(argv)}` fails on the merge base ")
                               for m in box.messages()):
                        box.enqueue(message_class="failure_report", origin=stem, stage=stage,
                                    outcome="base_red", summary=summary,
                                    occurrence_id=arrival_id("base-red", stem, attempt, stage, n))
        finally:
            await ctx.git.worktree_remove(ctx.repo, base_worktree)
    evidence = await gather_safety_evidence(ctx, ticket, claimed)
    reports, findings = [], []
    try:
        _validate_reports(_registered_files(outbox))
        if stage == "check":
            reports = [p.relative_to(worktree).as_posix() for p in _lift_files(ctx, stem, "checks")
                       if p.name in KNOWN_ARTIFACTS and p.name != "run.md"]
        elif not evidence.changed_files:
            from chupa.merge import lifted_report_paths

            reports = await lifted_report_paths(ctx, stem, attempt)
    except ArtifactInvalid as error:
        findings.append(Finding(code="verification", path=str(error.path.relative_to(worktree)),
                                message=f"invalid registered artifact: {error.error}",
                                paved_road="produce a schema-valid registered report through Verification"))
    if stage != "check":
        findings.extend(Finding(
            code="verification", path=f"{TICKETS_DIR}/{stem}/{name}",
            message=f"Verification named {name} but left no report in the outbox",
            paved_road="make the named Verification command exit 0 and write its registered report",
        ) for name in KNOWN_ARTIFACTS
            if any(f"{TICKETS_DIR}/{stem}/{name}" in arg for argv in ticket.verification for arg in argv)
            and not (outbox / name).is_file())
    if not evidence.changed_files and claimed == "ok":
        findings.extend(Finding(code="verification", path=p, message="uncommitted code in a report-only run",
                                paved_road="commit code on the branch and rerun Check, or remove the edit")
                        for p in await dirty_code(ctx, stem))
    return evidence.model_copy(update={"verification": results, "report_paths": reports,
                                       "report_findings": findings})


async def gather_safety_evidence(
    ctx: StageContext, ticket: Ticket, claimed: Literal["ok", "already_satisfied"],
) -> Evidence:
    """Gather the committed metadata once, without verification or base-worktree execution."""
    stem = ticket.stem
    worktree = ctx.worktree(stem)
    run_md = ctx.repo / TICKETS_DIR / stem / "run.md"
    changed = await ctx.git.diff_names(ctx.repo, MAIN, stem)
    anchored = PLAN_FILE in changed and any("#" in f for f in ticket.scope_fence)
    return Evidence(
        stem=stem,
        head_sha=await ctx.git.rev_parse(ctx.repo, stem),
        claimed=claimed,
        scope_fence=list(ticket.scope_fence),
        changed_files=changed,
        inserted_lines=_inserted(await ctx.git.diff(ctx.repo, MAIN, stem)),
        verification=[],
        run_record=run_md.read_text() if run_md.is_file() else None,
        plan_main=(ctx.repo / PLAN_FILE).read_text() if anchored else None,
        plan_head=(worktree / PLAN_FILE).read_text() if anchored else None,
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
                   and not (p.startswith(outbox) and p != outbox + TICKET_FILE)
                   and not (p == PLAN_FILE and self._unit_confined(artifact))]
        return _report(self.code, [
            Finding(code=self.code, path=p, message=f"{p} is outside `## Scope fence`",
                    paved_road="revert the edit and commit; if the criteria force it, reply premise_failed"
                               " naming the file so the fence is widened")
            for p in outside
        ])

    @staticmethod
    def _unit_confined(artifact: Evidence) -> bool:
        """A plan diff is admitted only when everything outside all anchored units is unchanged."""
        if artifact.plan_main is None or artifact.plan_head is None:
            return False
        units = [f.partition("#")[2] for f in artifact.scope_fence if f.startswith(PLAN_FILE + "#")]
        main, head = artifact.plan_main, artifact.plan_head
        for unit in units:
            main, head = without_unit(main, unit), without_unit(head, unit)
        return bool(units) and main == head


class VerificationGate:
    """The ticket's own `## Verification` commands, with base-red failures attributed to main.

    An empty `ok` diff needs current checks-lift report custody (19.P3.outbox-only-admission).
    """

    code = "verification"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        findings = [*artifact.report_findings, *[
            Finding(code=self.code, message=f"`{' '.join(r.argv)}` exited {r.rc}: {r.tail.strip() or '(no output)'}",
                    paved_road=f"make `{' '.join(r.argv)}` exit 0 on the branch and commit the fix")
            for r in artifact.verification if r.rc != 0 and not r.base_red
        ]]
        empty = not artifact.changed_files
        if empty and artifact.claimed == "ok" and (not artifact.report_paths or
                                                   any(r.rc != 0 for r in artifact.verification)):
            findings.append(Finding(code=self.code, message="the branch carries no committed change",
                                    paved_road="commit code on the branch, produce a registered report through"
                                               " Verification and leave it uncommitted for the checks lift, or"
                                               " reply already_satisfied if every criterion already holds"))
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


VERDICT_SIGNAL = "requisition_verdict"
APPROVED_SEEDS = "## Approved seeds (keep verbatim)"


def _seed_verdicts(ctx: StageContext, stem: str) -> dict[str, Mapping]:
    """Each seed's latest `requisition_verdict` inside the seeding ticket's lineage (section 19 PRIOR REVIEW)."""
    return {e.ticket: e.body for e in lineage(ctx.driver.journal.read(), stem)
            if e.type == EventType.SIGNAL and e.ticket is not None
            and e.body.get("signal") == VERDICT_SIGNAL and e.body.get("seeding") == stem}


def _prior_review(verdict: Mapping | None, text: str) -> str:
    if verdict is None:
        return "none"
    items = "\n".join(f"- [{f['code']}] ({f.get('kind')}) {_one_line(f['message'])}"
                      for f in verdict.get("findings", [])) or "- none"
    diff = "".join(difflib.unified_diff(verdict["text"].splitlines(keepends=True), text.splitlines(keepends=True),
                                        "judged", "current")) or "(unchanged)"
    return f"Verdict: {verdict['verdict']}\nFindings:\n{items}\n\nDiff from the judged text:\n{diff}"


def _restore_approved_seeds(ctx: StageContext, stem: str, worktree: Path) -> list[str]:
    """APPROVAL STICKS: an approved, unlifted seed re-enters the retry's fresh worktree byte-identical."""
    kept = []
    for seed, verdict in sorted(_seed_verdicts(ctx, stem).items()):
        rel = ticket_path(seed)
        if verdict["verdict"] == "approve" and not (ctx.repo / rel).exists():
            ctx.fs.write(worktree / rel, verdict["text"].encode())
            kept.append(rel)
    return kept


def _seeded_stems(ctx: StageContext, stem: str) -> set[str]:
    return {e.ticket for e in ctx.driver.journal.read()
            if e.type == EventType.SIGNAL and e.ticket is not None
            and e.body.get("signal") == "ticket_intake" and e.body.get("seeded_by") == stem}


async def _prior_seed_reviews(ctx: StageContext, stem: str, own: set[str]) -> dict[str, SeedReview]:
    path = f"{TICKETS_DIR}/{stem}/checks.json"
    try:
        text = await ctx.git._run(ctx.repo, "show", f"{MAIN}:{path}")
    except GitError:
        return {}
    invoice = Invoice.model_validate_json(text)
    return {seed.stem: seed for seed in invoice.seeds if seed.stem in own and seed.verdict == "approve"}


async def _review_seeds(ctx: StageContext, ticket: Ticket, *, attempt: int,
                        own: set[str], prior: dict[str, SeedReview]) -> tuple[list[SeedReview], list[Path]]:
    """Judge only new or changed ticket.md files; an identical foreign main file is not a candidate."""
    stem = ticket.stem
    worktree = ctx.worktree(stem)
    plan = (ctx.repo / PLAN_FILE).read_text()
    verdicts = _seed_verdicts(ctx, stem)
    reviews = dict(prior)
    new_paths: list[Path] = []
    candidates = sorted(p for p in (worktree / TICKETS_DIR).glob(f"*/{TICKET_FILE}")
                        if p.parent.name != stem)
    candidate_index = 0
    for path in candidates:
        seed_stem = path.parent.name
        rel = ticket_path(seed_stem)
        data = path.read_bytes()
        sha = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        try:
            main_sha = await ctx.git.rev_parse(ctx.repo, f"{MAIN}:{rel}")
        except GitError:
            main_sha = None
        if main_sha == sha and (seed_stem not in own or
                                (seed_stem in reviews and reviews[seed_stem].ticket_sha == sha)):
            continue
        candidate_index += 1
        earlier = verdicts.get(seed_stem)
        if earlier is not None and earlier["verdict"] == "approve" and earlier["ticket_sha"] == sha:
            # An approve holds while the bytes match: no re-review (section 19).
            reviews[seed_stem] = SeedReview(stem=seed_stem, ticket_sha=sha, verdict="approve", findings=[],
                                            mechanical="approved earlier")
            if main_sha is None:
                new_paths.append(path)
            continue
        review = await _review_one(ctx, ticket, seed_stem, rel, data, sha, main_sha, plan, worktree, earlier,
                                   siblings={p.parent.name for p in candidates} - {seed_stem},
                                   attempt=attempt, call_seq=candidate_index)
        reviews[seed_stem] = review
        text = data.decode(errors="replace")
        ctx.driver.journal.append(EventType.SIGNAL, {
            "signal": VERDICT_SIGNAL, "seeding": stem, "verdict": review.verdict, "ticket_sha": sha,
            "findings": [f.model_dump(mode="json", exclude_none=True) for f in review.findings], "text": text,
        }, ticket=seed_stem)
        if main_sha is None and review.verdict == "approve":
            new_paths.append(path)
    return [reviews[key] for key in sorted(reviews)], new_paths


async def _review_one(ctx: StageContext, ticket: Ticket, seed_stem: str, rel: str, data: bytes, sha: str,
                      main_sha: str | None, plan: str, worktree: Path, earlier: Mapping | None, *,
                      siblings: set[str], attempt: int, call_seq: int) -> SeedReview:
    """One seed's verdict: mechanical refusals first, then the requisition_review call with its prior review."""
    from chupa.requisition import review_ticket  # requisition imports implement_inputs from this module

    def snag(message: str, road: str, mechanical: str, kind: str = "authoring_error") -> SeedReview:
        finding = Finding(code="requisition_review", path=rel, message=message, paved_road=road, kind=kind)
        return SeedReview(stem=seed_stem, ticket_sha=sha, verdict="snag", findings=[finding], mechanical=mechanical)

    if main_sha is not None and main_sha != sha:
        return snag(f"{rel} already exists on main", "a seeding run only creates new stems; use a fresh stem",
                    "existing stem")
    # Read citations without resolving them: a missing registry entry must gap before grammar refuses it.
    sections, _ = _sections(data.decode(errors="replace"), rel)
    bullets, _ = _bullets(sections.get("Plan contract", ""), "Plan contract", rel)
    citations = []
    for bullet in bullets:
        try:
            citations.append(plan_id(bullet))
        except PlanContractError:
            pass  # Grammar reports malformed ids after the SPEC DEPTH check.
    units = required_units(plan, seed_stem, citations)
    gaps = [Finding(code="requisition_review", path=rel, message=gap,
                    paved_road="harden the entry unit through section 11.4; never invent its facts in the seed",
                    kind="spec_gap", unit=uid)
            for uid in units if (gap := entry_unit_gap(plan, uid)) is not None]
    if gaps:
        return SeedReview(stem=seed_stem, ticket_sha=sha, verdict="snag", findings=gaps,
                          mechanical="entry unit gap")
    outside_contract = []
    fence = in_contract = False
    for line in data.decode(errors="replace").splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and (heading := _HEADING.match(line)):
            in_contract = heading.group(1) == "Plan contract"
        if not in_contract:
            outside_contract.append(line)
    seed_body = _one_line("\n".join(outside_contract))
    for uid in citations:
        try:
            resolved = resolve_plan_contract(plan, [uid])
        except PlanContractError:
            continue  # Grammar reports ids that do not resolve.
        for line in resolved.splitlines():
            normalized = _one_line(line)
            if len(normalized) >= 60 and normalized in seed_body:
                return snag(f'cited unit {uid} text copied: "{normalized[:80]}"',
                            "cite the unit in `## Plan contract`; never copy its text", "unit text copied")
    try:
        parsed = validate_ticket(seed_stem, data.decode(), ctx.repo, siblings)
    except UnicodeDecodeError:
        return snag("ticket.md is not UTF-8", "write UTF-8 ticket text", "ticket lint failed")
    except TicketInvalid as exc:
        findings = [f.model_copy(update={"kind": "authoring_error"}) for f in exc.findings]
        return SeedReview(stem=seed_stem, ticket_sha=sha, verdict="snag", findings=findings,
                          mechanical="ticket lint failed")
    findings = []
    if parsed.frontmatter.source != "seed":
        findings.append(Finding(code="requisition_review", path=rel, message="seed source must be seed",
                                paved_road="set frontmatter `source: seed`", kind="authoring_error"))
    if parsed.frontmatter.state != "confirmed":
        findings.append(Finding(code="requisition_review", path=rel, message="seed state must be confirmed",
                                paved_road="set frontmatter `state: confirmed`", kind="authoring_error"))
    if findings:
        return SeedReview(stem=seed_stem, ticket_sha=sha, verdict="snag", findings=findings,
                          mechanical="seed frontmatter")
    reviewed = await review_ticket(
        ctx.driver, repo=ctx.repo, plan=plan, stem=seed_stem, text=data.decode(), specs_dir=ctx.specs_dir,
        tier=parsed.frontmatter.agent_tier, stem_slot=ticket.stem, run_seq=attempt, attempt=attempt,
        call_seq=call_seq, prior=_prior_review(earlier, data.decode()), siblings=siblings,
     expected_budget=ticket.expected_minutes * 60.0)
    return SeedReview(stem=seed_stem, ticket_sha=reviewed.ticket_sha, verdict=reviewed.verdict,
                      findings=list(reviewed.findings), mechanical=reviewed.mechanical)


async def lift_seeds(ctx: StageContext, stem: str, paths: list[Path], *, attempt: int) -> None:
    """One ticket-plane commit for the approved new ticket.md paths, followed by per-seed intake events."""
    if not paths:
        return
    rels = [ticket_path(p.parent.name) for p in paths]

    async def commit() -> dict:
        for src, rel in zip(paths, rels, strict=True):
            ctx.fs.write(ctx.repo / rel, src.read_bytes())
            src.unlink()
        await ctx.git.add(ctx.repo, rels)
        await ctx.git.commit(ctx.repo, f"chupa({stem}): seeds", only=rels)
        return {"commit": await ctx.git.rev_parse(ctx.repo, MAIN)}

    key = f"ticket-plane/{stem}/{attempt}/seeds"
    committed = await ctx.driver.effects.run(commit, key=key, ticket=stem)
    for path in paths:
        seed_stem = path.parent.name
        if not any(e.type == EventType.SIGNAL and e.ticket == seed_stem
                   and e.body.get("signal") == "ticket_intake" and e.body.get("commit") == committed["commit"]
                   and e.body.get("seeded_by") == stem for e in ctx.driver.journal.read()):
            ctx.driver.journal.append(EventType.SIGNAL,
                                      {"signal": "ticket_intake", "source": "seed", "state": "confirmed",
                                       "new": True, "commit": committed["commit"], "seeded_by": stem},
                                      ticket=seed_stem)


async def check(ctx: StageContext, ticket: Ticket, slip: PackingSlip, *, attempt: int) -> StageResult:
    """Invoicing: run the mechanical gates on the branch head, write + lift `checks.json`."""
    stem = ticket.stem
    started = ctx.driver.clock()
    prior_wait = ctx.driver.provider_wait(stem, attempt)
    def active_seconds():
        return max(0, (ctx.driver.clock() - started).total_seconds()
                   - (ctx.driver.provider_wait(stem, attempt) - prior_wait))
    outbox = ctx.worktree(stem) / TICKETS_DIR / stem
    evidence = await gather_evidence(ctx, ticket, slip.outcome, attempt=attempt)
    gated = run_gates(CHECK_GATES, evidence, ctx.worktree(stem), severity=check_severity(ctx, ticket))
    required = [name for name in KNOWN_ARTIFACTS
                if any(f"{TICKETS_DIR}/{stem}/{name}" in arg
                       for argv in ticket.verification for arg in argv)]
    missing = [name for name in required if not (outbox / name).is_file()]
    required_report = _report("verification", [Finding(
        code="verification", path=f"{TICKETS_DIR}/{stem}/{name}",
        message=f"Verification named {name} but left no report in the outbox",
        paved_road="make the named Verification command exit 0 and write its registered report",
    ) for name in missing]) if missing else None
    seeding = TICKETS_DIR in ticket.scope_fence
    own = _seeded_stems(ctx, stem) if seeding else set()
    prior = await _prior_seed_reviews(ctx, stem, own) if seeding else {}
    seeds = [prior[key] for key in sorted(prior)]
    new_paths: list[Path] = []
    seed_report = None
    if seeding and gated.passed:
        seeds, new_paths = await _review_seeds(ctx, ticket, attempt=attempt, own=own, prior=prior)
        seed_findings = [finding for seed in seeds if seed.verdict != "approve" for finding in seed.findings]
        seed_report = _report("requisition_review", seed_findings)
    passed = gated.passed and not missing and (seed_report is None or seed_report.verdict == "pass")
    invoice = Invoice(
        produced_by_spec_version=CHECK_SPEC_VERSION, produced_at_sha=evidence.head_sha, stem=stem,
        passed=passed, changed_files=evidence.changed_files, inserted_lines=evidence.inserted_lines,
        bypassed=sorted({b.code for b in ticket.frontmatter.gate_bypass}),
        reports=[*gated.reports, *([required_report] if required_report is not None else []),
                 *([seed_report] if seed_report is not None else [])], seeds=seeds,
        verification=evidence.verification,
    )
    ctx.fs.write(ctx.worktree(stem) / TICKETS_DIR / stem / "checks.json",
                 (invoice.model_dump_json(indent=2) + "\n").encode())
    try:
        await lift_outbox(ctx, stem, "checks", attempt=attempt)
    except ArtifactInvalid as error:
        error.path.unlink()
        (outbox / "checks.json").unlink(missing_ok=True)
        finding = Finding(code="verification", path=str(error.path.relative_to(ctx.worktree(stem))),
                          message=f"invalid registered artifact: {error.error}",
                          paved_road="produce the report through its named Verification command")
        return StageResult(outcome="gate_failed", artifact=invoice.model_copy(update={"passed": False}), findings=[finding],
                           cost=Cost(seconds=active_seconds()))
    except GitError as error:
        finding = Finding(code="verification", message=f"checks lift failed: {error}",
                          paved_road="repair the ticket-plane Git failure and rerun Check")
        return StageResult(outcome="gate_failed", artifact=invoice.model_copy(update={"passed": False}),
                           findings=[finding], cost=Cost(seconds=active_seconds()))
    if passed:
        await lift_seeds(ctx, stem, new_paths, attempt=attempt)
    cost = Cost(seconds=active_seconds())
    if not passed:
        hard = [f for r in gated.hard_failures for f in r.findings]
        if required_report is not None:
            hard.extend(required_report.findings)
        if seed_report is not None:
            hard.extend(seed_report.findings)
        return StageResult(outcome="gate_failed", artifact=invoice, findings=hard, cost=cost)
    outcome = "already_satisfied" if slip.outcome == "already_satisfied" else "ok"
    return StageResult(outcome=outcome, artifact=invoice, findings=gated.findings, cost=cost)


# --- Review -------------------------------------------------------------------------------------


def review_stage(ctx: StageContext, ticket_text: str, diff: str) -> tuple[LlmStage, Spec]:
    """specs/review.md wired UNCHANGED: the same spec and inputs the review baseline measured."""
    spec = _spec(ctx, "review")

    def render_diff(_: object, findings: list[Finding]) -> str:
        inputs = {"ticket": ticket_text, "diff": diff, "retry_findings": findings_text(findings)}
        return render(spec, inputs)

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
        # The effective ticket capability applies to every call in this attempt.
        result = await ctx.driver.run(
            stage, invoice, ticket=stem, attempt=attempt, workspace=ctx.worktree(stem),
            tier=ticket.frontmatter.agent_tier, effort=ticket.frontmatter.agent_effort,
            stuck_budget=ticket.stuck_minutes * 60.0,
            expected_budget=ticket.expected_minutes * 60.0, scope_fence=())
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
    boundary = ctx.boundary
    run = boundary.run or StagesRun(attempt=run_seq(ctx.driver.journal.read(), ticket.stem))
    boundary.ticket, boundary.next_stage = ticket, None
    for stage in ("implement", "check", "review"):
        if stage in run.results:
            if run.results[stage].outcome != "ok":
                return run
            continue
        if boundary.select is not None and not boundary.select(ticket, stage):
            boundary.run, boundary.next_stage = run, stage
            return run
        if stage == "implement":
            operation = implement(ctx, ticket, attempt=run.attempt)
        elif stage == "check":
            slip = run.results["implement"].artifact
            assert isinstance(slip, PackingSlip)
            operation = check(ctx, ticket, slip, attempt=run.attempt)
        else:
            invoice = run.results["check"].artifact
            assert isinstance(invoice, Invoice)
            operation = review(ctx, ticket, invoice, attempt=run.attempt)
        try:
            if boundary.select is None:
                result = await operation
            else:
                boundary.active = asyncio.create_task(operation)
                try:
                    result = await asyncio.shield(boundary.active)
                except asyncio.CancelledError:
                    await ctx.abort_current()
                    raise
                finally:
                    boundary.active = None
        except Exception as exc:
            from chupa.providers import ProviderCallError, ProviderDrought
            from chupa.driver import ProviderDroughtResult
            if isinstance(exc, ProviderDrought):
                result = ProviderDroughtResult(outcome='infra_error', artifact=None, findings=[],
                                               cost=Cost(), provider_drought=exc.record)
            elif isinstance(exc, ProviderCallError):
                findings = await ctx.driver.provider_failure(exc, owner=ticket.stem, ticket=ticket.stem,
                    sequence=run.attempt, surface='requisition_review', workspace=ctx.worktree(ticket.stem))
                meter = ctx.driver.detector.call if ctx.driver.detector else None
                result = StageResult(outcome='infra_error', artifact=None, findings=findings,
                    cost=Cost(attempts=1, provider=meter.identity[0] if meter else None,
                              model=meter.identity[1] if meter else None))
            else:
                raise
        run.results[stage] = result
        if result.outcome != "ok":
            break
    return run
