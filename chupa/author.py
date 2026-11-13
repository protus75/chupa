"""The Suggestion Box Author stage."""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from chupa.artifacts import Finding
from chupa.baseline import resolve_baseline
from chupa.box import Box, BoxError, DecisionRecord, Message, Resolution, record_path, render_record
from chupa.driver import Driver, LlmStage, unwrap_fence
from chupa.gates import GateReport
from chupa.git import GitError
from chupa.inbox import CAPS, bounded, report_data
from chupa.journal import EventType
from chupa.policy import policy_row, start_state
from chupa.requisition import FIRST_REVIEW, RequisitionVerdict, render_prior_review, review_ticket
from chupa.runner import SPECS_DIR, Checkout
from chupa.specs import Spec, load_spec, render
from chupa.stages import findings_text
from chupa.status import last_states
from chupa.tickets import TicketInvalid, split_frontmatter, stamp, stem_findings, template, ticket_path, validate_ticket

AUTHOR_STUCK_S = 900.0
NonBlank = Annotated[str, Field(min_length=1, pattern=r"\S")]


class AuthorReply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    stem: NonBlank
    ticket: NonBlank


class AuthorGate:
    code = "ticket_schema"

    def __init__(self, checkout: Checkout, message_class: str = "suggestion", *, remove=shutil.rmtree) -> None:
        self.checkout = checkout
        self.message_class = message_class
        self.message: Message | None = None
        self.copied: dict[str, list[str]] = {}
        self.passed_stems: set[str] = set()
        self._remove = remove

    def cleanup(self) -> None:
        """Remove only candidate directories this gate created, through an injected seam."""
        for stem in list(self.copied):
            directory = self.checkout.repo / "tickets" / stem
            if directory.exists():
                self._remove(directory)
            del self.copied[stem]

    def check(self, artifact: BaseModel, workspace: Path) -> GateReport:
        assert isinstance(artifact, AuthorReply)
        if self.copied and artifact.stem not in self.copied:
            self.cleanup()
        findings = list(stem_findings(artifact.stem))
        path = ticket_path(artifact.stem)
        if (self.checkout.repo / "tickets" / artifact.stem).exists() and artifact.stem not in self.copied:
            findings.append(Finding(code=self.code, path=path, message=f"stem {artifact.stem!r} already exists", paved_road="choose a new, never-before-used ticket stem"))
        if artifact.stem not in self.passed_stems and any(event.ticket == artifact.stem for event in self.checkout.journal.read()):
            findings.append(Finding(code=self.code, path=path, message=f"stem {artifact.stem!r} is already named in the journal", paved_road="choose a new, never-before-used ticket stem"))
        try:
            message = self.message
            if message is not None and message.report is not None and not findings:
                # Reserve ownership before writing so partial copies unwind too.
                paths = self.copied.setdefault(artifact.stem, [])
                for kind in CAPS:
                    if (source := getattr(message.report.custody, kind)) is not None:
                        data = bounded(self.checkout.config.state_dir / "box", source, kind)
                        target = f"tickets/{artifact.stem}/evidence/" + ("replay.json" if kind == "replay" else "log.txt")
                        self.checkout.fs.write(self.checkout.repo / target, data)
                        if target not in paths:
                            paths.append(target)
                report_path = f"tickets/{artifact.stem}/evidence/report.json"
                self.checkout.fs.write(self.checkout.repo / report_path, message.report.report.model_dump_json().encode())
                if report_path not in paths:
                    paths.append(report_path)
            candidate = artifact.ticket
            if split_frontmatter(candidate) is not None:
                candidate = stamp(stamp(candidate, "source", f"box:{self.message_class}"), "state", "draft")
            parsed = validate_ticket(artifact.stem, candidate, self.checkout.repo)
            if message is not None and message.report is not None:
                if parsed.frontmatter.kind != "bug":
                    findings.append(Finding(code=self.code, path=path, message="host report requires kind: bug", paved_road="author a bug ticket with one regression command and carries prefixes"))
                if message.bug_origin == "player" and message.summary in split_frontmatter(candidate)[1]:
                    findings.append(
                        Finding(code=self.code, path=path, message="raw player prose appears in ticket body", paved_road="write your own summary; cite the delimited evidence file instead")
                    )
        except TicketInvalid as exc:
            findings.extend(exc.findings)
        except (OSError, ValueError) as exc:
            findings.append(Finding(code=self.code, path=path, message=f"report custody refused: {exc}", paved_road="repair bounded Box custody before authoring a bug ticket"))
        if findings:
            self.cleanup()
        else:
            self.passed_stems.add(artifact.stem)
        return GateReport(code=self.code, verdict="fail" if findings else "pass", findings=findings)


@dataclass(frozen=True)
class AuthorOutcome:
    stem: str | None = None
    declined: str | None = None


def goal(text: str) -> str:
    after = text.partition("## Goal / Why\n")[2]
    return next((line.strip() for line in after.splitlines() if line.strip()), "")


async def committed(checkout: Checkout, path: Path) -> bool:
    try:
        await checkout.git.rev_parse(checkout.repo, f"HEAD:{path}")
    except GitError:
        return False
    return True


async def list_open_tickets(checkout: Checkout) -> str:
    states = last_states(checkout.journal.read())
    lines = []
    for path in sorted((checkout.repo / "tickets").glob("*/ticket.md")):
        stem = path.parent.name
        if states.get(stem) != "merged" and await committed(checkout, path.relative_to(checkout.repo)):
            lines.append(f"{stem}: {goal(path.read_text())}")
    return "\n".join(lines)


async def commit_record(checkout: Checkout, driver: Driver, record_id: str) -> None:
    path = record_path(record_id)

    async def commit() -> None:
        await checkout.git.commit(checkout.repo, f"chupa(decisions): {record_id}", only=[str(path)])

    await driver.effects.run(commit, key=f"ticket-plane/decisions/{record_id}", ticket=None)


async def failure_declined(checkout: Checkout, driver: Driver, box: Box, message: Message, evidence: str) -> AuthorOutcome:
    record_id = f"declined-{message.id}"
    record = DecisionRecord(id=record_id, kind="declined", link=message.id, reopen_after_days=30)
    body = f"Author could not produce a ticket.\n\nEvidence: {evidence}\n"
    checkout.fs.write(checkout.repo / record_path(record_id), render_record(record, body).encode())
    await commit_record(checkout, driver, record_id)
    box.resolve(message.id, Resolution(kind="declined", link=record_id))
    return AuthorOutcome(declined=record_id)


def record_retro_ticket(journal, message: Message, stem: str) -> None:
    if message.message_class != "retro_finding":
        return
    body = {"kind": "retro_ticket_authored", "box_id": message.id, "retro_report_key": message.retro_report_key, "ticket_stem": stem}
    key = f"retro-ticket/{stem}"
    history = journal.read()
    boundary = max(
        (i for i, e in enumerate(history) if e.type == EventType.EFFECT_INTENT and (e.key or "").startswith(f"retro-recurrence/{message.id}/") and e.body.get("reopened") is True), default=-1
    )
    prior = [
        e
        for i, e in enumerate(history)
        if e.key == key or (e.body.get("kind") == "retro_ticket_authored" and (e.body.get("ticket_stem") == stem or (e.body.get("box_id") == message.id and (not message.reopen or i > boundary))))
    ]
    if prior:
        if len(prior) != 1 or prior[0].type != EventType.SIGNAL or prior[0].key != key or prior[0].ticket != stem or prior[0].body != body:
            raise BoxError("conflicting retro ticket provenance; restore the Author-produced bridge before resolving the Box")
        return
    journal.append(EventType.SIGNAL, body, ticket=stem, key=key)


async def recover_retro_ticket(checkout: Checkout, box: Box, message: Message) -> AuthorOutcome | None:
    """Finish the bridge/resolution crash window without another Author invocation."""
    if message.message_class != "retro_finding":
        return None
    history = checkout.journal.read()
    boundary = max(
        (i for i, e in enumerate(history) if e.type == EventType.EFFECT_INTENT and (e.key or "").startswith(f"retro-recurrence/{message.id}/") and e.body.get("reopened") is True), default=-1
    )
    stems = set()
    for event in history[boundary + 1 :]:
        parts = (event.key or "").split("/")
        if event.type != EventType.EFFECT_COMPLETION or len(parts) != 6 or parts[:2] != ["llm", "author"] or parts[3:5] != ["author", str(message.seq)]:
            continue
        try:
            proposal = AuthorReply.model_validate_json(unwrap_fence(event.body["result"]["text"]))
        except ValueError:
            continue
        commit = next((e for e in history if e.type == EventType.EFFECT_COMPLETION and e.key == f"ticket-plane/{proposal.stem}/author"), None)
        if commit is not None:
            text = await checkout.git._run(checkout.repo, "show", f"{commit.body['result']}:{ticket_path(proposal.stem)}")
            if validate_ticket(proposal.stem, text, checkout.repo).frontmatter.source != "box:retro_finding":
                raise BoxError("conflicting committed retro ticket source; restore the Author-produced ticket and bridge")
            stems.add(proposal.stem)
    if not stems:
        return None
    if len(stems) != 1:
        raise BoxError("conflicting retro author completions; restore the unique Author-produced ticket provenance")
    stem = stems.pop()
    record_retro_ticket(checkout.journal, message, stem)
    box.resolve(message.id, Resolution(kind="ticket", link=stem))
    return AuthorOutcome(stem=stem)


async def author(checkout: Checkout, driver: Driver, box: Box, message: Message, pass_no: int) -> AuthorOutcome:
    """Author and ticket-plane commit one recorded author verdict."""
    try:
        row = policy_row(message.message_class, message.bug_origin, message.has_repro)
    except ValueError as exc:
        return await failure_declined(checkout, driver, box, message, str(exc))
    assert message.verdict is not None
    spec: Spec = load_spec((SPECS_DIR / "author.md").read_text())
    files = "\n".join(await checkout.git.ls_files(checkout.repo))
    try:
        report = report_data(message.report, box.root) if message.report else None
    except (OSError, ValueError) as exc:
        return await failure_declined(checkout, driver, box, message, f"report custody refused: {exc}")
    request = json.dumps(
        {
            "class": message.message_class,
            "rationale": message.verdict.rationale,
            "summary": message.summary,
            "retro_report_key": message.retro_report_key,
            "fixed_failure": message.fixed_failure,
            "overcorrection_risk": message.overcorrection_risk,
            "proposed_spec_paths": [f"chupa/{path}" for path in message.proposed_spec_paths],
            "test_issue": message.test_issue,
            "proposed_paths": message.proposed_paths,
            "reopen": message.reopen,
            "report": report,
        }
    )

    def render_author(_: object, findings: list) -> str:
        inputs = {
            "guide": (Path(__file__).parent / "docs" / "host-authoring.md").read_text(),
            "skeletons": "\n".join(f"{kind}:\n{template(kind)}" for kind in ("feature", "chore", "bug")),
            "request": request,
            "files": files,
            "open_tickets": open_tickets,
            "retry_findings": findings_text(findings),
            "previous_reply": previous_reply if previous_reply is not None else "none",
        }
        return render(spec, inputs)

    open_tickets = await list_open_tickets(checkout)
    previous_reply: str | None = None
    next_unused = 1
    reviewed: RequisitionVerdict | None = None
    reviewed_text: str | None = None
    reviewed_state: str | None = None
    author_gate = AuthorGate(checkout, message.message_class)
    author_gate.message = message

    async def review_candidate(artifact: BaseModel, call_seq: int) -> GateReport:
        nonlocal reviewed, reviewed_text, reviewed_state, next_unused, previous_reply
        assert isinstance(artifact, AuthorReply)
        previous_reply = artifact.ticket
        if author_gate.check(artifact, checkout.repo).verdict == "fail":
            # Grammar-invalid candidates never spend a requisition review call.
            return GateReport(code="requisition_review", verdict="pass")
        provisional = stamp(stamp(artifact.ticket, "source", f"box:{message.message_class}"), "state", "draft")
        parsed = validate_ticket(artifact.stem, provisional, checkout.repo)
        state = start_state(
            checkout.config,
            row=row,
            fence=parsed.scope_fence,
            gate_bypass=parsed.frontmatter.gate_bypass,
            go=resolve_baseline(checkout.config, checkout.journal.read(), specs_dir=SPECS_DIR).binds,
            reopen=message.reopen,
        )
        text = stamp(provisional, "state", state)
        start = max(call_seq, next_unused)
        reviewed = await review_ticket(
            driver,
            repo=checkout.repo,
            stem=artifact.stem,
            text=text,
            specs_dir=SPECS_DIR,
            coverage_map=checkout.config.state_dir / "coverage-map.json" if checkout.config.review.coverage_map is not None else None,
            tier=checkout.config.routing_default_tier,
            stem_slot="author",
            run_seq=pass_no,
            attempt=message.seq,
            call_seq=start,
            expected_budget=AUTHOR_STUCK_S / 2,
            prior=FIRST_REVIEW if reviewed is None else render_prior_review(reviewed.verdict, [f.model_dump() for f in reviewed.findings], reviewed_text, text),
        )
        next_unused = start + reviewed.calls
        reviewed_text = text
        reviewed_state = state
        findings = reviewed.findings
        if reviewed.verdict != "approve":
            author_gate.cleanup()
        if reviewed.verdict == "rma":
            findings = [finding.model_copy(update={"code": "requisition_rma"}) for finding in findings]
        return GateReport(code="requisition_review", verdict="pass" if reviewed.verdict == "approve" else "fail", findings=findings)

    checkout.journal.append(EventType.SIGNAL, {"signal": "author_invoked", "message": message.id})
    try:
        result = await driver.run(
            LlmStage(surface="author", emits=AuthorReply, gates=[author_gate], render=render_author, review=review_candidate, terminal_findings=frozenset({"requisition_rma"})),
            None,
            ticket=None,
            run_seq=pass_no,
            attempt=message.seq,
            workspace=checkout.repo,
            tier=checkout.config.routing_default_tier,
            effort=spec.meta.effort,
            stuck_budget=AUTHOR_STUCK_S,
            expected_budget="surface",
            scope_fence=(),
        )
    except BaseException:
        author_gate.cleanup()
        raise
    if result.outcome != "ok" or not isinstance(result.artifact, AuthorReply):
        author_gate.cleanup()
        return await failure_declined(checkout, driver, box, message, findings_text(result.findings) or result.outcome)
    reply = result.artifact
    assert reviewed is not None and reviewed_text is not None and reviewed_state is not None
    text = reviewed_text
    path = ticket_path(reply.stem)

    async def commit() -> str:
        paths = [path, *author_gate.copied.get(reply.stem, [])]
        return await checkout.git.commit(checkout.repo, f"chupa({reply.stem}): ticket", only=paths)

    try:
        checkout.fs.write(checkout.repo / path, text.encode())
        sha = await driver.effects.run(commit, key=f"ticket-plane/{reply.stem}/author", ticket=None)
    except BaseException as exc:
        if reply.stem in author_gate.copied:
            paths = [path, *author_gate.copied[reply.stem]]
            # Restore from HEAD: remove new index entries, but retain a commit
            # that landed before the Effects completion or SHA read failed.
            indexed = set(await checkout.git.ls_files(checkout.repo))
            staged = [p for p in paths if p in indexed]
            if staged:
                await checkout.git.restore(checkout.repo, staged, source="HEAD")
            try:
                await checkout.git.rev_parse(checkout.repo, f"HEAD:{path}")
            except GitError:
                author_gate.cleanup()
            else:
                author_gate.copied.clear()
        if not isinstance(exc, Exception):
            raise
        return await failure_declined(checkout, driver, box, message, f"commit failed: {type(exc).__name__}: {exc}")
    author_gate.copied.clear()
    checkout.journal.append(EventType.SIGNAL, {"signal": "ticket_intake", "source": f"box:{message.message_class}", "state": reviewed_state, "new": True, "commit": sha}, ticket=reply.stem)
    checkout.journal.append(
        EventType.SIGNAL,
        {"signal": "requisition_verdict", "verdict": "approve", "ticket_sha": reviewed.ticket_sha, "provider": reviewed.provider, "model": reviewed.model, "spec_version": reviewed.spec_version},
        ticket=reply.stem,
    )
    record_retro_ticket(checkout.journal, message, reply.stem)
    box.resolve(message.id, Resolution(kind="ticket", link=reply.stem))
    return AuthorOutcome(stem=reply.stem)
