"""The Implement, Check, and Review stages.

Implement and Review are prompt specs run through the one driver; Check is mechanical. This module
owns stage-evidence gathering and the stage-terminal OUTBOX lift: each
stage writes its artifact into `tickets/<stem>/` inside the worktree, and at the stage terminal the
lift moves it to the canonical tickets dir as ONE ticket-plane commit `chupa(<stem>): <kind>`.

The run's terminal `state_transition` is not written here: that is the runner's.
"""

import ast
import asyncio
import fnmatch
import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from chupa.artifacts import (
    DAEMON_SOAK_REPORT,
    EXIT_RECEIPT,
    HOST_LOOP_REPORT,
    OUTCOMES,
    RELIABILITY_BATTERY_REPORT,
    REVIEW_BASELINE_REPORT,
    SHAKEOUT_REPORT,
    Artifact,
    Cost,
    DaemonSoakReport,
    Diagnosis,
    DiagnosisReply,
    ExitReceipt,
    Finding,
    Harvest,
    HostLoopReport,
    NonBlank,
    Outcome,
    ReliabilityBatteryReport,
    ReviewBaselineReport,
    ReviewVerdict,
    ShakeoutReport,
    StageResult,
)
from chupa.box import BOX_DIR
from chupa.config import Config, ConfigSnapshot, Severity
from chupa.driver import Driver, LlmStage
from chupa.gates import BugEvidence, GateReport, RegressionRun, run_gates
from chupa.git import Git, GitError
from chupa.hostfiles import CORE_TEMPLATE, CoreDriftGate, committed_core
from chupa.journal import EventType, run_seq
from chupa.providers import child_env
from chupa.seams import ExecutableNotFound, FileSystem, ProcessExec
from chupa.specs import RenderOverBound, Spec, load_spec, render
from chupa.storm import arrival_id
from chupa.tickets import _HEADING, TEST_FIXTURE_DIRS, TICKET_FILE, TICKETS_DIR, Ticket, context_excerpt, context_path, ticket_path
from chupa.tickets import validate_ticket as validate_ticket

MAIN = "main"
KNOWN_ARTIFACTS: Mapping[str, type[BaseModel]] = {
    SHAKEOUT_REPORT: ShakeoutReport,
    DAEMON_SOAK_REPORT: DaemonSoakReport,
    RELIABILITY_BATTERY_REPORT: ReliabilityBatteryReport,
    REVIEW_BASELINE_REPORT: ReviewBaselineReport,
    HOST_LOOP_REPORT: HostLoopReport,
    EXIT_RECEIPT: ExitReceipt,
}
# Diff budget: sized so every rendered review prompt fits the serving provider's bound.
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
# The attempt-scoped re-entry block's heading, rendered in criteria-position.
PRIOR_ATTEMPTS = "## Prior attempts (attempt-scoped, informational, unverified, not reviewed)"
DIAGNOSIS_STUCK_S = 600.0


class _Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


# --- artifacts ----------------------------------------------------------------------------------


class SecondProblem(_Strict):
    summary: NonBlank


class ImplementReply(_Strict):
    """The implement surface's model-facing reply (chupa/specs/implement.md); the stage stamps provenance."""

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
    """Implement's artifact: the branch plus its run record."""

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
    # Historical checks.json files contain seed reviews; retro and triage parse them through Invoice.
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
    lines += [f"- [{f.code}] {f.path or '-'}:{f.line or '-'} {f.message} (do instead: {f.paved_road})" for f in review.findings] or ["none"]
    return "\n".join(lines + ["", "## Record", "", "```json", review.model_dump_json(indent=2), "```", ""])


def read_review(text: str) -> ApprovedInvoice | SnagList | Rma:
    """Parse `review.md`'s pinned record (the merge gate's on-disk input); the prose above it is not read."""
    m = _REVIEW_JSON.search(text)
    if m is None:
        raise ValueError("review.md carries no ```json record block; re-run Review to rewrite it")
    return _REVIEW.validate_json(m.group(1))


async def served_review(ctx, stem: str, attempt: int, reviewed: str) -> tuple[str | None, str | None]:
    """Only the approving call and its committed lift can attest to the served pair."""
    from chupa.driver import unwrap_fence

    try:
        events = ctx.driver.journal.read()
        path = f"tickets/{stem}/review.md"
        lifts = [e.body["result"] for e in events if e.type == EventType.EFFECT_COMPLETION and e.ticket == stem and e.key == f"ticket-plane/{stem}/{attempt}/review"]
        if len(lifts) != 1 or lifts[0]["kind"] != "review" or path not in lifts[0]["paths"]:
            return None, None
        commit = lifts[0]["commit"]
        pinned = await ctx.git._run(ctx.repo, "show", f"{MAIN}:{path}")
        if await ctx.git.merge_base(ctx.repo, MAIN, commit) != commit or pinned != await ctx.git._run(ctx.repo, "show", f"{commit}:{path}"):
            return None, None
        review = read_review(pinned)
        if not isinstance(review, ApprovedInvoice) or review.stem != stem or review.reviewed_sha != reviewed:
            return None, None
        calls = [e for e in events if e.type == EventType.EFFECT_COMPLETION and e.ticket == stem and e.key and re.fullmatch(rf"llm/{re.escape(stem)}/{attempt}/review/{attempt}/[1-9][0-9]*", e.key)]
        if not calls:
            return None, None
        call = calls[-1]
        if any(e.key == call.key and e.body != call.body for e in calls):
            return None, None
        result = call.body["result"]
        verdict = ReviewVerdict.model_validate_json(unwrap_fence(result["text"]))
        pair = result["provider"], result["model"]
        if (
            verdict.verdict != "approve"
            or verdict.summary != review.summary
            or verdict.findings != review.findings
            or pair != (review.provider, review.model)
            or any(not isinstance(n, str) or not n.strip() for n in pair)
            or any(call.body["cost"].get(k) != result[k] for k in ("provider", "model"))
        ):
            return None, None
        return pair
    except ValueError, KeyError, TypeError, AttributeError, GitError:
        return None, None


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


def ticket_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


async def ticket_change_findings(ctx: StageContext, stem: str, *, expected: str | None = None) -> list[Finding]:
    """Only ticket.md belongs to the dispatch identity; lifts may freely move main."""
    if expected is None:
        latest = next((e.body for e in reversed(ctx.driver.journal.read()) if e.type == EventType.STATE_TRANSITION and e.ticket == stem), {})
        if latest.get("to") == "running":
            expected = latest.get("ticket_sha")
    if expected is None:
        return []
    rel = ticket_path(stem)
    try:
        committed = await ctx.git.rev_parse(ctx.repo, f"{MAIN}:{rel}")
        unchanged = committed == expected and ticket_blob((ctx.repo / rel).read_bytes()) == expected
    except GitError, OSError:
        unchanged = False
    if unchanged:
        return []
    return [
        Finding(
            code="ticket_changed",
            path=rel,
            message=f"{stem}: ticket.md changed during the run",
            paved_road=f"review the change to {rel}, then keep (./dev.py confirm {stem}) or kill (./dev.py reject {stem})",
        )
    ]


class ArtifactInvalid(Exception):
    def __init__(self, path: Path, error: Exception) -> None:
        super().__init__(f"{path}: {error}")
        self.path = path
        self.error = error


class Stages:
    """Public access to the Driver already owned by the stage composition."""

    def __init__(self, ctx: StageContext):
        self._ctx = ctx

    @property
    def driver(self) -> Driver:
        return self._ctx.driver


def _registered_files(outbox: Path) -> list[Path]:
    return [p for p in outbox.rglob("*") if p.is_file() and p.name in KNOWN_ARTIFACTS]


def _lift_files(ctx: StageContext, stem: str, kind: str, only: str | None = None) -> list[Path]:
    outbox = ctx.worktree(stem) / TICKETS_DIR / stem
    canonical = ctx.repo / TICKETS_DIR / stem
    return sorted(
        p
        for p in outbox.rglob("*")
        if p.is_file()
        and p.relative_to(outbox) != Path(TICKET_FILE)
        and (only is None or p.relative_to(outbox).as_posix() == only)
        and (p.name not in KNOWN_ARTIFACTS or kind == "checks")
        and not ((c := canonical / p.relative_to(outbox)).is_file() and c.read_bytes() == p.read_bytes())
    )


def _validate_reports(paths: Sequence[Path]) -> None:
    for path in paths:
        if path.name in KNOWN_ARTIFACTS:
            try:
                KNOWN_ARTIFACTS[path.name].model_validate_json(path.read_bytes())
            except Exception as error:
                raise ArtifactInvalid(path, error) from error


async def dirty_code(ctx: StageContext, stem: str) -> list[str]:
    # NUL records preserve filenames and include both sides of a staged rename.
    records = iter((await ctx.git.status_porcelain(ctx.worktree(stem), "--untracked-files=all", "-z")).rstrip("\0").split("\0"))
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


async def write_diagnosis(
    ctx: StageContext, ticket: Ticket, *, attempt: int, terminal: str, stage: str | None, verdict: str, lessons: list[str], mechanical: str | None, cost: Cost = Cost()
) -> Diagnosis:
    spec = _spec(ctx, "diagnose")
    record = Diagnosis(
        produced_by_spec_version=_major(spec),
        produced_at_sha=await ctx.git.rev_parse(ctx.repo, ticket.stem),
        stem=ticket.stem,
        attempt=attempt,
        terminal=terminal,
        stage=stage,
        verdict=verdict,
        lessons=lessons,
        mechanical=mechanical,
        spec_version=spec.meta.version,
        provider=cost.provider,
        model=cost.model,
    )
    ctx.fs.write(ctx.worktree(ticket.stem) / TICKETS_DIR / ticket.stem / "diagnosis.json", (record.model_dump_json(indent=2) + "\n").encode())
    await lift_outbox(ctx, ticket.stem, "diagnosis", attempt=attempt, only="diagnosis.json")
    return record


async def diagnose(ctx: StageContext, ticket: Ticket, material: DiagnosisMaterial, *, attempt: int) -> Diagnosis:
    spec = _spec(ctx, "diagnose")
    result = await ctx.driver.run(
        diagnose_stage(spec, material),
        material,
        ticket=ticket.stem,
        attempt=attempt,
        workspace=ctx.worktree(ticket.stem),
        tier=ticket.frontmatter.agent_tier,
        effort=ticket.frontmatter.agent_effort,
        stuck_budget=DIAGNOSIS_STUCK_S,
        expected_budget=ticket.expected_minutes * 60.0,
        scope_fence=(),
    )
    reply = result.artifact
    if result.outcome == "ok" and isinstance(reply, DiagnosisReply):
        return await write_diagnosis(
            ctx, ticket, attempt=attempt, terminal=material.terminal, stage=material.stage, verdict=reply.verdict, lessons=list(reply.lessons), mechanical=None, cost=result.cost
        )
    return await write_diagnosis(
        ctx, ticket, attempt=attempt, terminal=material.terminal, stage=material.stage, verdict="abandon-human", lessons=[], mechanical=f"no schema-valid verdict ({result.outcome})", cost=result.cost
    )


def _short(result: StageResult, outcome: Outcome, findings: list[Finding], artifact: Artifact | None = None) -> StageResult:
    return StageResult(outcome=outcome, artifact=artifact, findings=findings, cost=result.cost)


async def prepare_worktree(ctx: StageContext, stem: str) -> Path:
    """TEARDOWN-AND-CREATE: remove any worktree and branch a prior run left, then branch from main."""
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


async def _base_worktree(ctx: StageContext, kind: str, stem: str, base: str) -> Path:
    assert ctx.config.worktree_root is not None  # resolved at config load
    path = ctx.config.worktree_root / kind / stem
    if path.exists():
        await ctx.git.worktree_remove(ctx.repo, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    await ctx.git.worktree_add_detached(ctx.repo, path, base)
    return path


async def lift_outbox(ctx: StageContext, stem: str, kind: str, *, attempt: int, only: str | None = None) -> str | None:
    """Move the worktree outbox into the canonical ticket dir as ONE ticket-plane commit; None if empty.

    `ticket.md` is never lifted: it stays read-only to the agent. Keyed with the run
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


def implement_inputs(repo: Path, ticket_text: str, ticket: Ticket, context_files: Sequence[Path]) -> dict[str, str]:
    """The production Implement inputs, also used to measure a ticket at authoring."""
    paths = list(dict.fromkeys([*ticket.context, *(str(p) for p in context_files)]))
    context = "\n\n".join(f"### {p}\n{context_excerpt(p, (repo / context_path(p)).read_text()) if p in ticket.context else (repo / p).read_text()}" for p in paths) or "none"
    return {
        "ticket": ticket_text,
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
    """Re-entry: the prior terminal and its findings as a clear-these block; None on a first attempt.

    Folded fresh from the journal and the ticket dir every attempt, never written into `ticket.md`. Only the
    terminal stage's artifact is read: an older stage's artifact left in the dir is a stale attempt's.
    """
    history = ctx.driver.journal.read()
    from chupa.journal import run_terminals

    terminals = [e.body for e in run_terminals(history, stem)]
    lessons = {e.body.get("attempt"): e.body["lessons"] for e in history if e.type == EventType.SIGNAL and e.ticket == stem and e.body.get("signal") == "diagnosis" and e.body.get("lessons")}
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
    head = (
        f"{PRIOR_ATTEMPTS}\n\nThe previous attempt ended `{terminal['to']}`{where}. These findings are"
        " this attempt's to clear, beside the acceptance criteria above; they are not part of the ticket.\n\n"
    )
    items = [f"- [{f.code}] {f.path or '-'}:{f.line or '-'} {_one_line(f.message)} (do instead: {_one_line(f.paved_road)})" for f in findings]
    detail = f"tickets/{stem}/attempts/{attempt}/" if current else str(ctx.config.state_dir / "engine.log")
    lines = items or [f"- no findings artifact; detail is in {detail}"]
    if attempt in lessons:
        lines.extend(["\nPrior terminal lessons (untrusted data):", *[f"> {_one_line(item)}" for item in lessons[attempt]]])
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
            lines.append(f"- older attempt {older}: `{past.terminal}` at {past.stage or 'none'}; tickets/{stem}/attempts/{older}/")
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


def implement_stage(ctx: StageContext, ticket: Ticket, worktree: Path) -> tuple[LlmStage, Spec]:
    spec = _spec(ctx, "implement")
    ticket_text = (ctx.repo / ticket_path(ticket.stem)).read_text()
    if (prior := prior_attempts(ctx, ticket.stem)) is not None:
        ticket_text = _in_criteria_position(ticket_text, prior)
    inputs = implement_inputs(worktree, ticket_text, ticket, ctx.config.context_files)

    def render_ticket(_: Ticket, findings: list[Finding]) -> str:
        return render(spec, {**inputs, "retry_findings": findings_text(findings)})

    return LlmStage(surface="implement", emits=ImplementReply, gates=[], render=render_ticket), spec


def run_record(reply: ImplementReply | None, cost: Cost, spec: Spec, second_problem_ids: Sequence[str], *, outcome: Outcome | None = None) -> str:
    fields = {
        "Outcome": outcome or reply.outcome,
        "Surprises / judgment calls": reply.surprises if reply else "none",
        "Dead ends": reply.dead_ends if reply else "none",
        "Second problems filed": "\n".join(f"- {id}: {_one_line(problem.summary)}" for id, problem in zip(second_problem_ids, reply.second_problems if reply else (), strict=True)) or "none",
        "Resolved engine/model": f"- provider: {cost.provider}\n- model: {cost.model}\n- spec: {spec.meta.llm_surface} {spec.meta.version}",
        "Predicted vs actual": reply.predicted_vs_actual if reply else "none",
    }
    return "".join(f"## {name}\n\n{(fields[name].strip() or 'none')}\n\n" for name in RUN_RECORD_SECTIONS)


async def implement(ctx: StageContext, ticket: Ticket, *, attempt: int) -> StageResult:
    """Teardown-and-create the worktree, run the implement spec in it, and write + lift the run record."""
    stem = ticket.stem
    worktree = await prepare_worktree(ctx, stem)
    stage, spec = implement_stage(ctx, ticket, worktree)
    try:
        result = await ctx.driver.run(
            stage,
            ticket,
            ticket=stem,
            attempt=attempt,
            workspace=worktree,
            tier=ticket.frontmatter.agent_tier,
            effort=ticket.frontmatter.agent_effort,
            stuck_budget=ticket.stuck_minutes * 60.0,
            expected_budget=ticket.expected_minutes * 60.0,
            scope_fence=ticket.scope_fence,
        )
    except RenderOverBound as e:
        # The pre-call short-circuit: ticket-text arithmetic, parked like premise_failed.
        return StageResult(outcome="premise_failed", artifact=None, findings=[e.finding], cost=Cost())
    if result.outcome != "ok":
        if result.cost.provider is not None:
            record = f"{TICKETS_DIR}/{stem}/run.md"
            ctx.fs.write(worktree / record, run_record(None, result.cost, spec, [], outcome=result.outcome).encode())
            await lift_outbox(ctx, stem, "run-record", attempt=attempt)
        return result
    reply = result.artifact
    assert isinstance(reply, ImplementReply)
    from chupa.daemon import storm_producer

    box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock)
    second_problem_ids = [
        box.enqueue(message_class="suggestion", origin=stem, stage="implement", outcome=reply.outcome, summary=problem.summary, occurrence_id=arrival_id("second-problem", stem, attempt, index))[0]
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
        stem=stem,
        branch=stem,
        outcome=reply.outcome,
        summary=reply.summary,
        run_record=record,
    )
    return _short(result, "ok", [], slip)


# --- Check --------------------------------------------------------------------------------------


class CommandResult(_Strict):
    argv: list[str]
    rc: int | None  # None: the command could not run or timed out -- fails closed like a nonzero exit
    tail: str
    base_red: bool = False
    seconds: float | None = None


async def run_host_command(ctx, ticket, attempt, argv, code, name, *, cwd=None):
    road = "make the configured command exit 0 on the rebased candidate and retry"
    started = ctx.driver.clock()
    try:
        rc, out, err = await ctx.exec_.run(argv, cwd=cwd or ctx.worktree(ticket.stem), env=child_env(ctx.env, ctx.config), timeout=ticket.stuck_minutes * 60.0)
    except TimeoutError:
        rc, out, err = None, "", f"timed out after the ticket's stuck budget ({ticket.stuck_minutes}m)"
        road = "make the command finish within the ticket's stuck budget or correct that budget and retry"
    except ExecutableNotFound as exc:
        rc, out, err = None, "", str(exc)
        road = "install the executable or correct argv/PATH in the child environment and retry"
    seconds = (ctx.driver.clock() - started).total_seconds()
    ctx.driver.spool.write(ticket.stem, attempt, name, f"$ {' '.join(argv)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
    tail = ctx.driver.redactor.scrub((out + err)[-OUTPUT_TAIL_CHARS:])
    result = CommandResult(argv=list(argv), rc=rc, tail=tail, base_red=False, seconds=seconds)
    findings = [] if rc == 0 else [Finding(message=ctx.driver.redactor.scrub(f"{argv!r} exited {rc}: {tail.strip() or '(no output)'}"), paved_road=road, code=code)]
    return result, GateReport(code=code, verdict="fail" if findings else "pass", findings=findings)


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
    core_files: dict[str, bytes | None] = {}
    core_template: bytes = CORE_TEMPLATE
    core_findings: list[Finding] = []
    report_paths: list[str] = []
    report_findings: list[Finding] = []
    is_bug: bool = False
    bug_evidence: BugEvidence | None = None
    bug_findings: list[Finding] = []


def regression_result(stdout: str, rc: int | None) -> Literal["pass", "defect", "error"] | None:
    """Decode the complete common protocol, never a runner's diagnostic or exit vocabulary."""

    def unique(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("duplicate keys")
        return result

    if len(stdout) > OUTPUT_TAIL_CHARS:
        return None
    try:
        result = json.loads(stdout, object_pairs_hook=unique)
    except ValueError, TypeError, RecursionError:
        return None
    if not isinstance(result, dict) or set(result) != {"regression_result"}:
        return None
    value = result["regression_result"]
    if not isinstance(value, str) or value not in {"pass", "defect", "error"}:
        return None
    if (value == "pass" and rc == 0) or (value == "defect" and rc is not None and rc > 0):
        return value
    return "error" if value == "error" else None


def _bug_finding(message: str) -> Finding:
    return Finding(
        code="bug_evidence",
        message=message,
        paved_road="supply durable ticket evidence and carries matching only changed test/fixture files;"
        " provide a carried reproducer checking prerequisites and emitting the regression"
        " result protocol: pass at head, defect at the overlaid base",
    )


async def _gather_bug(ctx: StageContext, ticket: Ticket, evidence: Evidence, *, attempt: int, stage: str) -> tuple[BugEvidence, list[Finding]]:
    worktree = ctx.worktree(ticket.stem)
    base = await ctx.git.merge_base(ctx.repo, MAIN, ticket.stem)
    findings, overlay = [], set()
    for prefix in ticket.carries:
        path = Path(prefix)
        if not prefix or path.is_absolute() or ".." in path.parts or path.as_posix() != prefix.rstrip("/"):
            findings.append(_bug_finding(f"invalid carries prefix {prefix!r}"))
            continue
        matched = [p for p in evidence.changed_files if _in_fence(p, [prefix])]
        if not matched:
            findings.append(_bug_finding(f"carries prefix {prefix!r} matches no branch-changed file"))
        for rel in matched:
            if not TEST_FIXTURE_DIRS.intersection(Path(rel).parts[:-1]):
                findings.append(_bug_finding(f"carries path {rel!r} is not a test/fixture file; implementation paths cannot be carried"))
                continue
            tree = await ctx.git._run(ctx.repo, "ls-tree", evidence.head_sha, "--", rel)
            if not tree.startswith(("100644 blob ", "100755 blob ")):
                findings.append(_bug_finding(f"carries path {rel!r} is not a committed regular file"))
                continue
            overlay.add(rel)
    custody = []
    for root in (ctx.repo, worktree):
        directory = root / TICKETS_DIR / ticket.stem / "evidence"
        custody.extend(p.relative_to(root).as_posix() for p in directory.rglob("*") if p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(directory.resolve()))
    record = BugEvidence(
        argv=[ctx.driver.redactor.scrub(arg) for arg in ticket.regression], head_sha=evidence.head_sha, base_sha=base, overlay_paths=sorted(overlay), evidence_paths=sorted(set(custody))
    )
    if not custody:
        findings.append(_bug_finding("durable evidence is missing under the ticket evidence/ directory"))
    if not ticket.regression or not ticket.carries:
        findings.append(_bug_finding("parsed regression command or carries set is missing"))
    if findings:
        return record, findings

    async def execute(root: Path, name: str) -> RegressionRun:
        try:
            rc, out, err = await ctx.exec_.run(list(ticket.regression), cwd=root, env=child_env(ctx.env, ctx.config), timeout=ticket.stuck_minutes * 60.0)
        except (TimeoutError, ExecutableNotFound, OSError) as error:
            rc, out, err = None, "", f"regression execution failed: {error}"
        decoded = regression_result(out, rc)
        ctx.driver.spool.write(ticket.stem, attempt, f"{stage}/regression-{name}.txt", f"$ {' '.join(ticket.regression)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
        return RegressionRun(rc=rc, regression_result=decoded, tail=ctx.driver.redactor.scrub(out + err)[-OUTPUT_TAIL_CHARS:])

    head = await execute(worktree, "head")
    base_worktree = await _base_worktree(ctx, ".regression-base", ticket.stem, base)
    try:
        # Restore committed blobs (including executable mode), never dirty checkout copies.
        for rel in overlay:
            if any(p.is_symlink() for p in (base_worktree / rel).parents if p.is_relative_to(base_worktree)):
                return record.model_copy(update={"head": head}), [_bug_finding("base overlay traverses a symlink")]
        await ctx.git.restore(base_worktree, sorted(overlay), source=evidence.head_sha)
        base_run = await execute(base_worktree, "base")
    except GitError as error:
        return record.model_copy(update={"head": head}), [_bug_finding(ctx.driver.redactor.scrub(f"cannot overlay regression inputs: {error}"))]
    finally:
        await ctx.git.worktree_remove(ctx.repo, base_worktree)
    return record.model_copy(update={"head": head, "base": base_run}), findings


def _inserted(diff: str) -> int:
    return sum(line.startswith("+") and not line.startswith("+++") for line in diff.splitlines())


async def gather_evidence(
    ctx: StageContext,
    ticket: Ticket,
    claimed: Literal["ok", "already_satisfied"],
    *,
    attempt: int,
    stage: str = "check",
) -> Evidence:
    stem = ticket.stem
    worktree = ctx.worktree(stem)
    outbox = worktree / TICKETS_DIR / stem
    for path in _registered_files(outbox):
        path.unlink()
    env = child_env(ctx.env, ctx.config)  # verification never inherits a provider key
    results = []
    red: list[tuple[int, list[str]]] = []
    timeout = ticket.stuck_minutes * 60.0
    for n, argv in enumerate(ticket.verification, 1):
        started = ctx.driver.clock()
        try:
            rc, out, err = await ctx.exec_.run(list(argv), cwd=worktree, env=env, timeout=timeout)
        except TimeoutError:
            rc, out, err = None, "", f"timed out after the ticket's stuck budget ({ticket.stuck_minutes}m)"
        except ExecutableNotFound as e:
            rc, out, err = None, "", str(e)
        seconds = (ctx.driver.clock() - started).total_seconds()
        ctx.driver.spool.write(stem, attempt, f"{stage}/verify-{n:02d}.txt", f"$ {' '.join(argv)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
        tail = ctx.driver.redactor.scrub((out + err)[-OUTPUT_TAIL_CHARS:])
        results.append(CommandResult(argv=list(argv), rc=rc, tail=tail, seconds=seconds))
        if rc != 0:
            red.append((n, list(argv)))
    if red:
        base = await ctx.git.merge_base(ctx.repo, MAIN, stem)
        base_worktree = await _base_worktree(ctx, ".base", stem, base)
        try:
            from chupa.daemon import storm_producer

            box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock)
            for n, argv in red:
                try:
                    rc, out, err = await ctx.exec_.run(argv, cwd=base_worktree, env=env, timeout=timeout)
                except TimeoutError:
                    rc, out, err = None, "", f"timed out after the ticket's stuck budget ({ticket.stuck_minutes}m)"
                except ExecutableNotFound as e:
                    rc, out, err = None, "", str(e)
                ctx.driver.spool.write(stem, attempt, f"{stage}/verify-{n:02d}-base.txt", f"$ {' '.join(argv)}\n[exit {rc}]\n--- stdout\n{out}\n--- stderr\n{err}")
                if rc != 0:
                    results[n - 1] = results[n - 1].model_copy(update={"base_red": True})
                    summary = f"`{' '.join(argv)}` fails on the merge base {base[:8]} too; fix main, not this ticket"
                    if not any(
                        m.message_class == "failure_report" and m.origin == stem and m.outcome == "base_red" and m.summary.startswith(f"`{' '.join(argv)}` fails on the merge base ")
                        for m in box.messages()
                    ):
                        box.enqueue(message_class="failure_report", origin=stem, stage=stage, outcome="base_red", summary=summary, occurrence_id=arrival_id("base-red", stem, attempt, stage, n))
        finally:
            await ctx.git.worktree_remove(ctx.repo, base_worktree)
    evidence = await gather_safety_evidence(ctx, ticket, claimed)
    reports, findings = [], []
    try:
        _validate_reports(_registered_files(outbox))
        if stage == "check":
            reports = [p.relative_to(worktree).as_posix() for p in _lift_files(ctx, stem, "checks") if p.name in KNOWN_ARTIFACTS and p.name != "run.md"]
        elif not evidence.changed_files:
            from chupa.merge import lifted_report_paths

            reports = await lifted_report_paths(ctx, stem, attempt)
    except ArtifactInvalid as error:
        findings.append(
            Finding(
                code="verification",
                path=str(error.path.relative_to(worktree)),
                message=f"invalid registered artifact: {error.error}",
                paved_road="produce a schema-valid registered report through Verification",
            )
        )
    if stage != "check":
        findings.extend(
            Finding(
                code="verification",
                path=f"{TICKETS_DIR}/{stem}/{name}",
                message=f"Verification named {name} but left no report in the outbox",
                paved_road="make the named Verification command exit 0 and write its registered report",
            )
            for name in KNOWN_ARTIFACTS
            if any(f"{TICKETS_DIR}/{stem}/{name}" in arg for argv in ticket.verification for arg in argv) and not (outbox / name).is_file()
        )
    if not evidence.changed_files and claimed == "ok":
        findings.extend(
            Finding(code="verification", path=p, message="uncommitted code in a report-only run", paved_road="commit code on the branch and rerun Check, or remove the edit")
            for p in await dirty_code(ctx, stem)
        )
    bug, bug_findings = await _gather_bug(ctx, ticket, evidence, attempt=attempt, stage=stage) if ticket.frontmatter.kind == "bug" else (None, [])
    return evidence.model_copy(update={"verification": results, "report_paths": reports, "report_findings": findings, "bug_evidence": bug, "bug_findings": bug_findings})


async def gather_safety_evidence(
    ctx: StageContext,
    ticket: Ticket,
    claimed: Literal["ok", "already_satisfied"],
) -> Evidence:
    """Gather the committed metadata once, without verification or base-worktree execution."""
    stem = ticket.stem
    worktree = ctx.worktree(stem)
    run_md = ctx.repo / TICKETS_DIR / stem / "run.md"
    changed = await ctx.git.diff_names(ctx.repo, MAIN, stem)
    return Evidence(
        stem=stem,
        head_sha=await ctx.git.rev_parse(ctx.repo, stem),
        claimed=claimed,
        scope_fence=list(ticket.scope_fence),
        changed_files=changed,
        inserted_lines=_inserted(await ctx.git.diff(ctx.repo, MAIN, stem)),
        verification=[],
        is_bug=ticket.frontmatter.kind == "bug",
        run_record=run_md.read_text() if run_md.is_file() else None,
        **await committed_core(worktree, ctx.config, ctx.git),
    )


def _report(code: str, findings: list[Finding]) -> GateReport:
    return GateReport(code=code, verdict="fail" if findings else "pass", findings=findings)


def _in_fence(path: str, prefixes: Sequence[str]) -> bool:
    return any(path == p or path.startswith(p if p.endswith("/") else p + "/") for p in prefixes)


def triggered_hosts(ctx, changed_files, *, hard_only=False):
    return [
        (n, entry)
        for n, entry in enumerate(ctx.config.review.mechanical, 1)
        if (not hard_only or entry.severity == "hard") and (entry.trigger == "always" or any(_in_fence(path, entry.trigger) for path in changed_files))
    ]


def _detection_letters(number):
    letters = ""
    while number:
        number, digit = divmod(number - 1, 26)
        letters = chr(ord("a") + digit) + letters
    return letters


def _changed_lines(diff: str) -> dict[str, set[int]]:
    lines: dict[str, set[int]] = {}
    path = None
    new_line = 0
    in_hunk = False
    body = diff.splitlines()
    for i, line in enumerate(body):
        if line.startswith("diff --git "):
            path = None
            new_line = 0
            in_hunk = False
        elif not in_hunk and line.startswith("+++ "):
            name = line[4:]
            if name.startswith('"'):
                name = ast.literal_eval("b" + name).decode("utf-8")
            path = name[2:] if name.startswith("b/") else None
        elif line.startswith("@@ "):
            in_hunk = True
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
            new_line = int(match[1]) if match else 0
        elif path is not None and new_line:
            if line.startswith("+"):
                lines.setdefault(path, set()).add(new_line)
                new_line += 1
            elif line.startswith("-"):
                if i == 0 or body[i - 1][:1] not in "+-":
                    end = i
                    while end < len(body) and body[end].startswith("-"):
                        end += 1
                    if end == len(body) or not body[end].startswith("+"):
                        lines.setdefault(path, set()).update((max(1, new_line - 1), max(1, new_line)))
            elif line.startswith(" "):
                new_line += 1
    return lines


def coverage_contexts(report: dict) -> dict[str, dict[str, list[str]]]:
    files = report["files"]
    if not isinstance(files, dict):
        raise ValueError("invalid files")
    contexts = {}
    has_test_context = False
    for name, data in files.items():
        mapping = data["contexts"]
        if not isinstance(mapping, dict):
            raise ValueError("invalid contexts")
        for line, values in mapping.items():
            if not isinstance(line, str) or not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                raise ValueError("invalid contexts")
            has_test_context |= any("|" in value for value in values)
        contexts[name] = mapping
    if not has_test_context:
        raise ValueError("no test contexts")
    return contexts


async def _check_host_results(ctx, ticket, entry, n, attempt, changed_files):
    from chupa.covgate import percentages
    from chupa.daemon import flake_detection, storm_producer
    from chupa.flake import GreenRerunEvidence, RerunEvidence
    from chupa.gates import TestCoverage, TestTiming
    from chupa.testreport import ResultsInvalid, read_results, slow_tests

    root = ctx.worktree(ticket.stem)
    path = root / entry.results
    box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock)
    escalations = []
    flake = flake_detection(journal=ctx.driver.journal, box=box, config=ctx.config, escalate=escalations.append)

    async def run(name):
        path.unlink(missing_ok=True)
        result, report = await run_host_command(ctx, ticket, attempt, entry.argv, entry.code, name)
        try:
            results = read_results(path.read_text())
        except OSError, UnicodeError, ResultsInvalid:
            results = None
        return result, report, results

    def invalid():
        return _report(
            entry.code,
            [
                Finding(
                    code=entry.code,
                    path=entry.results,
                    message=f"Missing or invalid results file: {entry.results}",
                    paved_road=f"make the command write it via -p chupa.testreport --chupa-results {entry.results}",
                )
            ],
        )

    result, report, first = await run(f"check/host-{n:02d}.txt")
    if first is None:
        return invalid() if result.rc == 0 else report
    timing = TestTiming(
        seconds=result.seconds,
        passed=list(first.tests.values()).count("passed"),
        failed=list(first.tests.values()).count("failed"),
        skipped=list(first.tests.values()).count("skipped"),
        slow=slow_tests(first.seconds, entry.slow_test_seconds, entry.slow_test_limit),
    )
    coverage = None
    if entry.coverage is not None:
        try:
            percent, files = percentages(json.loads((root / entry.coverage).read_text()))
            coverage = TestCoverage(percent=percent, files={path: value for path, value in files.items() if path in changed_files})
        except OSError, UnicodeError, ValueError:
            pass

    def recorded(report):
        return report.model_copy(update={"timing": timing, "coverage": coverage})

    first = first.tests
    last = first
    if result.rc != 0 and "failed" in first.values():
        result, report, last = await run(f"check/host-{n:02d}-rerun.txt")
        if last is None:
            return invalid()
        last = last.tests
        projection = flake.quarantine()
        findings = []
        flaky = {test for test, outcome in first.items() if outcome == "failed" and last.get(test) == "passed"}
        covered = set()
        if flaky and entry.coverage is not None:
            try:
                contexts = coverage_contexts(json.loads((root / entry.coverage).read_text()))
            except OSError, UnicodeError, ValueError, KeyError, TypeError:
                return recorded(
                    _report(
                        entry.code,
                        [
                            Finding(
                                code=entry.code,
                                path=entry.coverage,
                                message=f"Missing or invalid coverage contexts: {entry.coverage}",
                                paved_road='run with --cov-context=test, and set [tool.coverage.json] show_contexts = true and [tool.coverage.run] core = "ctrace"',
                            )
                        ],
                    )
                )
            changed = _changed_lines(await ctx.git.diff(ctx.repo, MAIN, ticket.stem))
            covered = {context.split("|", 1)[0] for name, numbers in changed.items() for number in numbers for context in contexts.get(name, {}).get(str(number), []) if "|" in context}
        for test in sorted(flaky):
            edited = test.split("::", 1)[0] in changed_files or test in covered
            if edited:
                findings.append(Finding(code=entry.code, message=f"{test} is flaky and touches edited code", paved_road="make it deterministic by faking time, IO and ordering"))
            elif test not in projection.tests:
                count = 1 + sum(identity.test_id == test and box_id not in projection.active for box_id, identity in projection.detected.items())
                projection = flake.detect(
                    test_id=test,
                    evidence=RerunEvidence(test, "fail", "pass", True, True, True),
                    summary=f"{test} failed then passed for {ticket.stem}",
                    reason=f"failed then passed on a bare rerun; detection {_detection_letters(count)}",
                    occurrence_id=arrival_id("flake-detection", ticket.stem, attempt, test, n),
                )
                if test not in projection.tests:
                    findings.append(Finding(code=entry.code, message=f"{test}: {escalations[-1]}", paved_road="fix and release existing quarantines before admitting this test"))
        for test, outcome in sorted(last.items()):
            if outcome == "failed" and (test not in projection.tests or test.split("::", 1)[0] in changed_files):
                findings.append(Finding(code=entry.code, message=f"{test} failed on rerun", paved_road="fix the failing test"))
        if result.rc != 0 and "failed" not in last.values():
            findings.extend(report.findings)
        report = _report(entry.code, findings)

    events = ctx.driver.journal.read()
    for identity in list(flake.quarantine().active.values()):
        if last.get(identity.test_id) != "passed":
            continue
        message = box.get(identity.box_id)
        resolution = message.resolution
        fix = resolution.link if message.status == "resolved" and resolution is not None and resolution.kind == "ticket" else None
        if fix and any(event.type == EventType.STATE_TRANSITION and event.ticket == fix and event.body.get("to") == "merged" for event in events):
            flake.release(box_id=identity.box_id, evidence=GreenRerunEvidence(identity.test_id, fix, ctx.driver.clock(), "pass", True, True, True))
    return recorded(report)


async def check_hosts(ctx, ticket, changed_files, attempt):
    reports, hard = [], []
    for n, entry in triggered_hosts(ctx, changed_files):
        if entry.results is None:
            _, report = await run_host_command(ctx, ticket, attempt, entry.argv, entry.code, f"check/host-{n:02d}.txt")
        else:
            report = await _check_host_results(ctx, ticket, entry, n, attempt, changed_files)
        if report.verdict == "fail":
            base = await ctx.git.merge_base(ctx.repo, MAIN, ticket.stem)
            base_worktree = await _base_worktree(ctx, ".base", ticket.stem, base)
            try:
                if entry.results is not None:
                    (base_worktree / entry.results).unlink(missing_ok=True)
                baseline, _ = await run_host_command(ctx, ticket, attempt, entry.argv, entry.code, f"check/host-{n:02d}-base.txt", cwd=base_worktree)
                if entry.results is not None:
                    from chupa.testreport import ResultsInvalid, read_results

                    try:
                        read_results((base_worktree / entry.results).read_text())
                    except OSError, UnicodeError, ResultsInvalid:
                        pass
            finally:
                await ctx.git.worktree_remove(ctx.repo, base_worktree)
            if baseline.rc != 0:
                from chupa.daemon import storm_producer

                box = storm_producer(root=ctx.config.state_dir / BOX_DIR, fs=ctx.fs, journal=ctx.driver.journal, clock=ctx.driver.clock)
                prefix = ctx.driver.redactor.scrub(f"`{' '.join(entry.argv)}` fails on the merge base ")
                summary = f"{prefix}{base[:8]} too; fix main, not this ticket"
                if not any(m.message_class == "failure_report" and m.origin == ticket.stem and m.outcome == "base_red" and m.summary.startswith(prefix) for m in box.messages()):
                    box.enqueue(
                        message_class="failure_report", origin=ticket.stem, stage="check", outcome="base_red", summary=summary, occurrence_id=arrival_id("base-red", ticket.stem, attempt, "check", n)
                    )
                report = _report(entry.code, [])
            elif entry.severity == "hard":
                hard.extend(report.findings)
        reports.append(report)
    return reports, hard


class ScopeFenceGate:
    """The implement stage's write allowlist: the committed diff within `## Scope fence`.

    The stem's own outbox is exempt except `ticket.md`, which stays read-only to the agent.
    """

    code = "scope_fence"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        outbox = f"{TICKETS_DIR}/{artifact.stem}/"
        outside = [p for p in artifact.changed_files if not _in_fence(p, artifact.scope_fence) and not (p.startswith(outbox) and p != outbox + TICKET_FILE)]
        return _report(
            self.code,
            [
                Finding(
                    code=self.code,
                    path=p,
                    message=f"{p} is outside `## Scope fence`",
                    paved_road="revert the edit and commit; if the criteria force it, reply premise_failed naming the file so the fence is widened",
                )
                for p in outside
            ],
        )


class VerificationGate:
    """The ticket's own `## Verification` commands, with base-red failures attributed to main.

    An empty `ok` diff needs current checks-lift report custody.
    """

    code = "verification"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        findings = [
            *artifact.report_findings,
            *[
                Finding(
                    code=self.code, message=f"`{' '.join(r.argv)}` exited {r.rc}: {r.tail.strip() or '(no output)'}", paved_road=f"make `{' '.join(r.argv)}` exit 0 on the branch and commit the fix"
                )
                for r in artifact.verification
                if r.rc != 0 and not r.base_red
            ],
        ]
        empty = not artifact.changed_files
        if empty and artifact.claimed == "ok" and (not artifact.report_paths or any(r.rc != 0 for r in artifact.verification)):
            findings.append(
                Finding(
                    code=self.code,
                    message="the branch carries no committed change",
                    paved_road="commit code on the branch, produce a registered report through"
                    " Verification and leave it uncommitted for the checks lift, or"
                    " reply already_satisfied if every criterion already holds",
                )
            )
        if not empty and artifact.claimed == "already_satisfied":
            findings.append(
                Finding(
                    code=self.code,
                    message=f"already_satisfied was claimed but the branch carries a diff: {', '.join(artifact.changed_files)}",
                    paved_road="reply ok for a branch with changes; already_satisfied commits nothing",
                )
            )
        return _report(self.code, findings)


class RunRecordGate:
    """`run.md` present with the fixed section set and a closed-vocab `## Outcome`."""

    code = "run_record"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        path = f"{TICKETS_DIR}/{artifact.stem}/run.md"
        road = "re-run Implement so the engine writes run.md with every required section"
        if artifact.run_record is None:
            return _report(self.code, [Finding(code=self.code, path=path, message="run.md is missing", paved_road=road)])
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
            findings.append(Finding(code=self.code, path=path, message=f"run.md sections are {list(sections)}", paved_road=f"use exactly {list(RUN_RECORD_SECTIONS)}, in order"))
        outcome = "\n".join(sections.get("Outcome", [])).strip()
        if outcome not in OUTCOMES:
            findings.append(Finding(code=self.code, path=path, message=f"`## Outcome` {outcome!r} is not an outcome", paved_road=f"use one of {sorted(OUTCOMES)}"))
        return _report(self.code, findings)


class DiffBudgetGate:
    """A mechanical cap on the reviewable diff, so the review prompt fits its bound."""

    code = "diff_budget"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        files, inserted = len(artifact.changed_files), artifact.inserted_lines
        if files <= DIFF_BUDGET_FILES and inserted <= DIFF_BUDGET_INSERTED:
            return _report(self.code, [])
        return _report(
            self.code,
            [
                Finding(
                    code=self.code,
                    message=f"diff is {files} files / {inserted} inserted lines, over the budget of {DIFF_BUDGET_FILES} files / {DIFF_BUDGET_INSERTED} lines",
                    paved_road="split the ticket into smaller stems, each under the diff budget",
                )
            ],
        )


class BugEvidenceGate:
    """A new test proves a defect only when its carried reproducer reaches the defect on base."""

    code = "bug_evidence"

    def check(self, artifact: Evidence, workspace: Path) -> GateReport:
        if not artifact.is_bug:
            return _report(self.code, [])
        record = artifact.bug_evidence
        findings = list(artifact.bug_findings)
        if record is None:
            findings.append(_bug_finding("fresh regression evidence is missing"))
        elif not findings:
            if not record.evidence_paths:
                findings.append(_bug_finding("durable ticket evidence is missing"))
            if record.head_sha != artifact.head_sha:
                findings.append(_bug_finding("regression evidence pins a different candidate head"))
            if record.head is None or record.head.rc != 0 or record.head.regression_result != "pass":
                findings.append(_bug_finding("regression head did not complete with exit 0 and pass"))
            if record.base is None or record.base.rc is None or record.base.rc <= 0 or record.base.regression_result != "defect":
                findings.append(_bug_finding("overlaid base did not complete with a positive exit and defect"))
        return GateReport(code=self.code, verdict="fail" if findings else "pass", findings=findings, bug_evidence=record)


CHECK_GATES: tuple[ScopeFenceGate | VerificationGate | RunRecordGate | DiffBudgetGate | CoreDriftGate | BugEvidenceGate, ...] = (
    ScopeFenceGate(),
    VerificationGate(),
    RunRecordGate(),
    DiffBudgetGate(),
    CoreDriftGate(),
    BugEvidenceGate(),
)


def check_severity(ctx: StageContext, ticket: Ticket) -> dict[str, Severity]:
    """Config severity with the ticket's `gate_bypass` valve applied: a bypassed code is soft for this ticket."""
    severity = dict(ctx.driver.severity)
    for bypass in ticket.frontmatter.gate_bypass:
        severity[bypass.code] = "soft"
    if ticket.frontmatter.source == "box:retro_finding":
        # Admission provenance is required even when the ticket demotes schema checks.
        severity["ticket_schema"] = "hard"
    return severity


async def check_autofix(ctx, ticket, attempt):
    worktree = ctx.worktree(ticket.stem)
    files = [path for path in await ctx.git.diff_names(ctx.repo, MAIN, ticket.stem) if not _in_fence(path, [TICKETS_DIR]) and (worktree / path).is_file()]
    selections = [[path for path in files if any(fnmatch.fnmatch(path, pattern) for pattern in entry.files)] for entry in ctx.config.review.autofix]
    selected = {path for paths in selections for path in paths}
    files = [path for path in files if path in selected]
    if not files:
        return [], []
    before = {path: (worktree / path).read_bytes() for path in files}
    reports = []
    for n, (entry, paths) in enumerate(zip(ctx.config.review.autofix, selections, strict=True), 1):
        if not paths:
            continue
        result, report = await run_host_command(ctx, ticket, attempt, [*entry.argv, *paths], entry.code, f"check/autofix-{n:02d}.txt")
        reports.append(report)
        if result.rc != 0:
            await ctx.git.restore(worktree, files, source=ticket.stem)
            return reports, report.findings
    changed = [path for path in files if (worktree / path).read_bytes() != before[path]]
    if changed:
        await ctx.git.add(worktree, changed)
        await ctx.git.commit(worktree, f"chupa({ticket.stem}): autofix", only=changed)
    return reports, []


async def check(ctx: StageContext, ticket: Ticket, slip: PackingSlip, *, attempt: int) -> StageResult:
    """Invoicing: run the mechanical gates on the branch head, write + lift `checks.json`."""
    stem = ticket.stem
    started = ctx.driver.clock()
    prior_wait = ctx.driver.provider_wait(stem, attempt)

    def active_seconds():
        return max(0, (ctx.driver.clock() - started).total_seconds() - (ctx.driver.provider_wait(stem, attempt) - prior_wait))

    outbox = ctx.worktree(stem) / TICKETS_DIR / stem
    autofix_reports, autofix_hard = await check_autofix(ctx, ticket, attempt) if slip.outcome == "ok" and ctx.config.review.autofix else ([], [])
    evidence = await gather_evidence(ctx, ticket, slip.outcome, attempt=attempt)
    gated = run_gates(CHECK_GATES, evidence, ctx.worktree(stem), severity=check_severity(ctx, ticket))
    host_reports, host_hard = await check_hosts(ctx, ticket, evidence.changed_files, attempt)
    host_hard.extend(autofix_hard)
    required = [name for name in KNOWN_ARTIFACTS if any(f"{TICKETS_DIR}/{stem}/{name}" in arg for argv in ticket.verification for arg in argv)]
    missing = [name for name in required if not (outbox / name).is_file()]
    required_report = (
        _report(
            "verification",
            [
                Finding(
                    code="verification",
                    path=f"{TICKETS_DIR}/{stem}/{name}",
                    message=f"Verification named {name} but left no report in the outbox",
                    paved_road="make the named Verification command exit 0 and write its registered report",
                )
                for name in missing
            ],
        )
        if missing
        else None
    )
    passed = gated.passed and not host_hard and not missing
    invoice = Invoice(
        produced_by_spec_version=CHECK_SPEC_VERSION,
        produced_at_sha=evidence.head_sha,
        stem=stem,
        passed=passed,
        changed_files=evidence.changed_files,
        inserted_lines=evidence.inserted_lines,
        bypassed=sorted({b.code for b in ticket.frontmatter.gate_bypass}),
        reports=[*autofix_reports, *gated.reports, *host_reports, *([required_report] if required_report is not None else [])],
        verification=evidence.verification,
    )
    ctx.fs.write(ctx.worktree(stem) / TICKETS_DIR / stem / "checks.json", (invoice.model_dump_json(indent=2) + "\n").encode())
    try:
        await lift_outbox(ctx, stem, "checks", attempt=attempt)
    except ArtifactInvalid as error:
        error.path.unlink()
        (outbox / "checks.json").unlink(missing_ok=True)
        finding = Finding(
            code="verification",
            path=str(error.path.relative_to(ctx.worktree(stem))),
            message=f"invalid registered artifact: {error.error}",
            paved_road="produce the report through its named Verification command",
        )
        return StageResult(outcome="gate_failed", artifact=invoice.model_copy(update={"passed": False}), findings=[finding], cost=Cost(seconds=active_seconds()))
    except GitError as error:
        finding = Finding(code="verification", message=f"checks lift failed: {error}", paved_road="repair the ticket-plane Git failure and rerun Check")
        return StageResult(outcome="gate_failed", artifact=invoice.model_copy(update={"passed": False}), findings=[finding], cost=Cost(seconds=active_seconds()))
    cost = Cost(seconds=active_seconds())
    if not passed:
        hard = [f for r in gated.hard_failures for f in r.findings]
        hard.extend(autofix_hard)
        hard.extend(f for r in host_reports for f in r.findings)
        if required_report is not None:
            hard.extend(required_report.findings)
        return StageResult(outcome="gate_failed", artifact=invoice, findings=hard, cost=cost)
    outcome = "already_satisfied" if slip.outcome == "already_satisfied" else "ok"
    return StageResult(outcome=outcome, artifact=invoice, findings=[*gated.findings, *(f for r in host_reports for f in r.findings)], cost=cost)


# --- Review -------------------------------------------------------------------------------------


def review_stage(ctx: StageContext, ticket_text: str, diff: str, prior_review: str) -> tuple[LlmStage, Spec]:
    """chupa/specs/review.md wired UNCHANGED: the same spec and inputs the review baseline measured."""
    spec = _spec(ctx, "review")

    def render_diff(_: object, findings: list[Finding]) -> str:
        inputs = {"ticket": ticket_text, "diff": diff, "prior_review": prior_review, "retry_findings": findings_text(findings)}
        return render(spec, inputs)

    return LlmStage(surface="review", emits=ReviewVerdict, gates=[], render=render_diff), spec


async def review(ctx: StageContext, ticket: Ticket, invoice: Invoice, *, attempt: int) -> StageResult:
    """Inspect: one separate-session review of `git diff main...<stem>`, pinned to the reviewed SHA.

    approve -> ok; snag and rma -> gate_failed (the review surface is a gate); the
    verdict-keyed artifact lands in `review.md` either way.
    """
    stem = ticket.stem
    reviewed = await ctx.git.rev_parse(ctx.repo, stem)
    diff = await ctx.git.diff(ctx.repo, MAIN, stem)
    prior_path = ctx.repo / TICKETS_DIR / stem / "review.md"
    try:
        prior = read_review(prior_path.read_text()) if prior_path.is_file() else None
    except ValueError:
        prior = None
    prior_review = findings_text(prior.findings) if isinstance(prior, SnagList) else "none"
    stage, spec = review_stage(ctx, (ctx.repo / ticket_path(stem)).read_text(), diff, prior_review)
    try:
        # The effective ticket capability applies to every call in this attempt.
        result = await ctx.driver.run(
            stage,
            invoice,
            ticket=stem,
            attempt=attempt,
            workspace=ctx.worktree(stem),
            tier=ticket.frontmatter.agent_tier,
            effort=ticket.frontmatter.agent_effort,
            stuck_budget=ticket.stuck_minutes * 60.0,
            expected_budget=ticket.expected_minutes * 60.0,
            scope_fence=(),
        )
    except RenderOverBound as e:
        return StageResult(outcome="premise_failed", artifact=None, findings=[e.finding], cost=Cost())
    if result.outcome != "ok":
        return result
    verdict = result.artifact
    assert isinstance(verdict, ReviewVerdict)
    artifact = EMITS_BY_VERDICT[verdict.verdict](
        produced_by_spec_version=_major(spec),
        produced_at_sha=reviewed,
        stem=stem,
        reviewed_sha=reviewed,
        verdict=verdict.verdict,
        summary=verdict.summary,
        findings=list(verdict.findings),
        spec_version=spec.meta.version,
        provider=result.cost.provider,
        model=result.cost.model,
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
    ticket_sha: str | None = None

    @property
    def last(self) -> tuple[StageName, StageResult]:
        return list(self.results.items())[-1]


async def run_stages(ctx: StageContext, ticket: Ticket) -> StagesRun:
    """Implement -> Check -> Review for one ticket, single worker, in the process holding the lock.

    `already_satisfied`, proven by Check's green verification on an empty diff, stops before Review:
    there is no diff to review and the ticket settles as a no-op.
    """
    boundary = ctx.boundary
    dispatched = next((e.body for e in reversed(ctx.driver.journal.read()) if e.type == EventType.STATE_TRANSITION and e.ticket == ticket.stem), {})
    run = boundary.run or StagesRun(
        attempt=run_seq(ctx.driver.journal.read(), ticket.stem),
        ticket_sha=(dispatched.get("ticket_sha") if dispatched.get("to") == "running" else None) or await ctx.git.rev_parse(ctx.repo, f"{MAIN}:{ticket_path(ticket.stem)}"),
    )
    boundary.ticket, boundary.next_stage = ticket, None
    for stage in ("implement", "check", "review"):
        if stage in run.results:
            if run.results[stage].outcome != "ok":
                return run
            continue
        if boundary.select is not None and not boundary.select(ticket, stage):
            boundary.run, boundary.next_stage = run, stage
            return run
        if findings := await ticket_change_findings(ctx, ticket.stem, expected=run.ticket_sha):
            run.results[stage] = StageResult(outcome="gate_failed", artifact=None, findings=findings, cost=Cost())
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
        if stage == "check":
            ctx.driver.log.event("stage_start", stem=ticket.stem, attempt=run.attempt, surface="check")
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
            from chupa.driver import ProviderDroughtResult
            from chupa.providers import ProviderCallError, ProviderDrought

            if isinstance(exc, ProviderDrought):
                result = ProviderDroughtResult(outcome="infra_error", artifact=None, findings=[], cost=Cost(), provider_drought=exc.record)
            elif isinstance(exc, ProviderCallError):
                findings = await ctx.driver.provider_failure(exc, owner=ticket.stem, ticket=ticket.stem, sequence=run.attempt, surface="requisition_review", workspace=ctx.worktree(ticket.stem))
                meter = ctx.driver.detector.call if ctx.driver.detector else None
                result = StageResult(
                    outcome="infra_error", artifact=None, findings=findings, cost=Cost(attempts=1, provider=meter.identity[0] if meter else None, model=meter.identity[1] if meter else None)
                )
            else:
                raise
        if stage == "check":
            ctx.driver.log.event("stage_end", stem=ticket.stem, attempt=run.attempt, surface="check", outcome=result.outcome)
        run.results[stage] = result
        if result.outcome != "ok":
            break
    return run
