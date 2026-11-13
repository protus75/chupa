"""Read-only authored-ticket feasibility review."""

import difflib
import hashlib
import json
import re
from contextlib import ExitStack
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from chupa.artifacts import Artifact, Finding, NonBlank
from chupa.driver import Driver, _StuckBudget, unwrap_fence
from chupa.gates import GateReport
from chupa.journal import EventType
from chupa.llm import AgentTier, LLMRequest, LLMResult
from chupa.llmeffect import llm_call
from chupa.providers import ProviderCallError, ProviderDrought
from chupa.specs import RENDER_BOUND_CHARS, REQ_RENDER_HEADROOM, RenderOverBound, load_spec, render
from chupa.stages import _in_fence, implement_inputs
from chupa.tickets import Ticket, TicketInvalid, lint_findings, validate_ticket

REQUISITION_STUCK_S = 600.0
FIRST_REVIEW = "first review: no earlier review recorded"


class Dependent(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    path: NonBlank
    status: Literal["fenced", "unaffected"]
    reason: NonBlank


class RequisitionReply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    verdict: Literal["approve", "snag", "rma"]
    summary: NonBlank
    findings: list[Finding]
    dependents: list[Dependent] = Field(default_factory=list)

    @model_validator(mode="after")
    def _findings_match_verdict(self) -> "RequisitionReply":
        if bool(self.findings) == (self.verdict == "approve"):
            raise ValueError("findings must be empty exactly for approve")
        return self


class RequisitionVerdict(Artifact):
    stem: NonBlank
    ticket_sha: NonBlank
    verdict: Literal["approve", "snag", "rma"]
    summary: NonBlank
    findings: list[Finding]
    render_chars: Annotated[int, Field(ge=0)]
    mechanical: str | None
    calls: int
    spec_version: NonBlank
    provider: str | None
    model: str | None


def test_sources(repo: Path) -> dict[str, str]:
    return {path.relative_to(repo).as_posix(): path.read_text() for path in (repo / "tests").rglob("*.py")}


def dependent_errors(reply: RequisitionReply, expected: set[str], fence: tuple[str, ...]) -> list[str]:
    paths = [entry.path for entry in reply.dependents]
    errors = [f"missing dependent: {path}" for path in sorted(expected - set(paths))]
    errors += [f"extra dependent: {path}" for path in sorted(set(paths) - expected)]
    errors += [f"duplicate dependent: {path}" for path in sorted(set(paths)) if paths.count(path) > 1]
    errors += [f"wrongly fenced dependent: {entry.path}" for entry in reply.dependents if entry.status == "fenced" and not _in_fence(entry.path, fence)]
    return errors


def review_target(repo: Path, stem: str, text: str) -> Ticket:
    """Use the complete ticket admission predicate, including reserved stems."""
    ticket = validate_ticket(stem, text, repo)
    if findings := lint_findings(ticket, repo):
        raise TicketInvalid(findings)
    return ticket


def _base_render(repo: Path, ticket: Ticket, text: str, specs_dir: Path) -> str:
    spec = load_spec((specs_dir / "implement.md").read_text())
    inputs = implement_inputs(repo, text, ticket, ())
    return render(spec, {**inputs, "retry_findings": "none"})


def base_render_chars(repo: Path, ticket: Ticket, text: str, specs_dir: Path) -> int:
    """Measure the same first-attempt Implement prompt that production renders, at max effort."""
    try:
        return len(_base_render(repo, ticket, text, specs_dir))
    except RenderOverBound as exc:
        # The renderer measured the complete prompt before refusing it.
        return int(re.search(r"rendered prompt is (\d+) characters", exc.finding.message).group(1))


async def prior_review(git, repo, events, stem, text) -> str:
    """Render the latest recorded findings and changes to the text they judged."""
    event = next((e for e in reversed(events) if e.type == EventType.SIGNAL and e.ticket == stem and e.body.get("signal") == "requisition_verdict" and "findings" in e.body), None)
    if event is None:
        return FIRST_REVIEW
    body = event.body
    judged = await git._run(repo, "show", body["ticket_sha"])
    return render_prior_review(body["verdict"], body["findings"], judged, text)


def render_prior_review(verdict, findings, judged, text) -> str:
    """Render a review and the changes made since it judged the text."""
    findings_text = "\n".join(f"- [{f['code']}] {' '.join(f['message'].splitlines())}" for f in findings) or "- none"
    diff = "".join(difflib.unified_diff(judged.splitlines(keepends=True), text.splitlines(keepends=True))) or "(unchanged)"
    return f"Verdict: {verdict}\nFindings:\n{findings_text}\n\nDiff from the judged text:\n{diff}"


async def review_ticket(
    driver: Driver,
    *,
    repo: Path,
    stem: str,
    text: str,
    specs_dir: Path,
    coverage_map: Path | None,
    tier: AgentTier,
    stem_slot: str,
    run_seq: int,
    attempt: int,
    call_seq: int,
    expected_budget: float | Literal["surface", "eval"],
    prior: str,
) -> RequisitionVerdict:
    spec = load_spec((specs_dir / "requisition_review.md").read_text())
    ticket_bytes = text.encode()
    sha = hashlib.sha1(f"blob {len(ticket_bytes)}\0".encode() + ticket_bytes).hexdigest()
    try:
        ticket = review_target(repo, stem, text)
    except TicketInvalid as exc:
        return RequisitionVerdict(
            produced_by_spec_version=int(spec.meta.version.split(".")[0]),
            produced_at_sha=sha,
            stem=stem,
            ticket_sha=sha,
            render_chars=0,
            spec_version=spec.meta.version,
            verdict="snag",
            summary="ticket lint failed",
            findings=exc.findings,
            mechanical="ticket lint",
            provider=None,
            model=None,
            calls=0,
        )
    try:
        base = _base_render(repo, ticket, text, specs_dir)
        chars = len(base)
    except RenderOverBound as exc:
        base = None
        chars = int(re.search(r"rendered prompt is (\d+) characters", exc.finding.message).group(1))
    common = dict(produced_by_spec_version=int(spec.meta.version.split(".")[0]), produced_at_sha=sha, stem=stem, ticket_sha=sha, render_chars=chars, spec_version=spec.meta.version)

    calls = 0

    def snag(message: str, mechanical: str, code: str = "requisition_review", road: str = "repair the ticket or review response and retry") -> RequisitionVerdict:
        return RequisitionVerdict(
            **common,
            verdict="snag",
            summary=message,
            findings=[Finding(code=code, message=message, paved_road=road, kind="authoring_error")],
            mechanical=mechanical,
            provider=None,
            model=None,
            calls=calls,
        )

    if chars > REQ_RENDER_HEADROOM * RENDER_BOUND_CHARS:
        return snag(f"base Implement render has {chars} characters, over authoring headroom", "render over headroom", "render_feasibility", "shrink or split the ticket at authoring")
    assert base is not None

    dependents: dict[str, set[str]] = {}
    reads: dict[str, set[str]] = {}
    coverage_dependents = "no coverage map configured"
    if coverage_map is not None:
        try:
            data = json.loads(coverage_map.read_text())
            files = data["files"]
            if not isinstance(files, dict) or any(not isinstance(path, str) or not isinstance(tests, list) or any(not isinstance(test, str) for test in tests) for path, tests in files.items()):
                raise ValueError("invalid files mapping")
        except OSError, UnicodeError, ValueError, KeyError, TypeError:
            return snag("missing or invalid coverage map", "invalid coverage map", "coverage_map", "run ./dev.py covmap")
        for path in ticket.scope_fence:
            for test in files.get(path, []):
                if not _in_fence(test, ticket.scope_fence):
                    dependents.setdefault(test, set()).add(path)
    data_paths = [path for path in ticket.scope_fence if not path.endswith(".py")]
    if data_paths:
        for test, source in test_sources(repo).items():
            if not _in_fence(test, ticket.scope_fence):
                for path in data_paths:
                    if path in source:
                        reads.setdefault(test, set()).add(path)
    lines = [f"{test}: runs {', '.join(sorted(paths))}" for test, paths in sorted(dependents.items())]
    lines += [f"{test}: reads {path}" for test, paths in sorted(reads.items()) for path in sorted(paths)]
    if lines or coverage_map is not None:
        coverage_dependents = "\n".join(lines) or "none"
    expected_dependents = set(dependents) | set(reads)

    event_context = dict(stem=stem, attempt=attempt, surface="requisition_review", run_seq=run_seq)
    outcome = "gate_failed"
    owns_watch = False
    with ExitStack() as stack:
        try:
            retry_findings = "none"
            for current_seq in range(call_seq, call_seq + driver.retry_cap + 1):
                try:
                    prompt = render(
                        spec, {"ticket": text, "context": "included in render", "render": base, "prior_review": prior, "retry_findings": retry_findings, "coverage_dependents": coverage_dependents}
                    )
                except RenderOverBound as exc:
                    return snag(str(exc), "review render over bound", road="shrink or split the ticket at authoring")

                name = f"requisition_review/call-{current_seq:02d}"
                spool_stem = f"{stem_slot}/{run_seq}"
                driver.spool.write(spool_stem, attempt, f"{name}/prompt.md", prompt)
                req = LLMRequest(surface="requisition_review", rendered=prompt, tier=tier, effort=spec.meta.effort, ticket=None, worktree=None)
                if driver._active is None:
                    if calls == 0:
                        owns_watch = True
                    driver.begin_watch(
                        owner=stem_slot,
                        ticket=None,
                        run_sequence=run_seq,
                        surface="requisition_review",
                        workspace=repo,
                        expected_budget=expected_budget,
                        stuck_budget=REQUISITION_STUCK_S,
                        scope_fence=(),
                        attempt=attempt,
                    )
                if calls == 0 and owns_watch:
                    event = stack.enter_context(driver.stage(**event_context))
                calls += 1
                try:
                    recorded = await driver.race(
                        lambda: llm_call(driver.effects, driver.watched_llm(), req, driver.redactor, ticket=stem, stem=stem_slot, run_seq=run_seq, attempt=attempt, call_seq=current_seq),
                        REQUISITION_STUCK_S,
                    )
                except _StuckBudget:
                    outcome = "timeout"
                    return snag("requisition review timed out", "timeout", road="retry the authoring review")
                except ProviderDrought, ProviderCallError:
                    raise
                except Exception as exc:
                    outcome = "infra_error"
                    message = f"requisition review provider failed: {type(exc).__name__}: {exc}"
                    driver.spool.write(spool_stem, attempt, f"{name}/error.txt", message)
                    return snag(message, "provider error", road="repair the provider and retry the authoring review")
                result = LLMResult(**recorded)
                driver.spool.write(spool_stem, attempt, f"{name}/output.txt", result.text)
                try:
                    reply = RequisitionReply.model_validate_json(unwrap_fence(result.text))
                except ValidationError as exc:
                    if calls <= driver.retry_cap:
                        retry_findings = f"Reply must be only the JSON object. {exc}"
                        continue
                    message = f"invalid requisition review reply: {exc.error_count()} schema error(s)"
                    return RequisitionVerdict(
                        **common,
                        calls=calls,
                        verdict="snag",
                        summary=message,
                        findings=[Finding(code="requisition_review", message=message, paved_road="reply with a schema-valid requisition verdict", kind="authoring_error")],
                        mechanical="invalid reply",
                        provider=result.provider,
                        model=result.model,
                    )
                errors = dependent_errors(reply, expected_dependents, ticket.scope_fence)
                if errors:
                    retry_findings = "; ".join(errors)
                    if calls <= driver.retry_cap:
                        continue
                    return RequisitionVerdict(
                        **common,
                        calls=calls,
                        verdict="snag",
                        summary="invalid requisition review reply: " + retry_findings,
                        findings=[Finding(code="requisition_review", message=retry_findings, paved_road="account for each listed dependent exactly once", kind="authoring_error")],
                        mechanical="invalid reply",
                        provider=result.provider,
                        model=result.model,
                    )
                outcome = "ok" if reply.verdict == "approve" else "gate_failed"
                return RequisitionVerdict(**common, calls=calls, verdict=reply.verdict, summary=reply.summary, findings=reply.findings, mechanical=None, provider=result.provider, model=result.model)
        except BaseException:
            outcome = "infra_error"
            raise
        finally:
            if calls and owns_watch:
                event.end(outcome, run_seq=run_seq, calls=calls)


class RequisitionGate:
    code = "requisition_review"

    def check(self, artifact: RequisitionVerdict, workspace: Path) -> GateReport:
        return GateReport(code=self.code, verdict="pass" if artifact.verdict == "approve" else "fail", findings=[] if artifact.verdict == "approve" else artifact.findings)
