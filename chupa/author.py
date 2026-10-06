"""The Suggestion Box Author stage (CHUPA_PLAN.md sections 12 and 13)."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from chupa.box import Box, DecisionRecord, Message, Resolution, record_path, render_record
from chupa.driver import Driver, LlmStage
from chupa.gates import GateReport
from chupa.journal import EventType
from chupa.policy import baseline_identity, go_binds, policy_row, start_state
from chupa.requisition import RequisitionVerdict, review_ticket
from chupa.runner import Checkout, SPECS_DIR
from chupa.specs import Spec, load_spec, render
from chupa.stages import findings_text
from chupa.tickets import TicketInvalid, split_frontmatter, stamp, stem_findings, ticket_path, validate_ticket

AUTHOR_STUCK_S = 900.0
NonBlank = Annotated[str, Field(min_length=1, pattern=r"\S")]


class AuthorReply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    stem: NonBlank
    ticket: NonBlank


class AuthorGate:
    code = "ticket_schema"

    def __init__(self, checkout: Checkout, message_class: str = "suggestion") -> None:
        self.checkout = checkout
        self.message_class = message_class

    def check(self, artifact: BaseModel, workspace: Path) -> GateReport:
        assert isinstance(artifact, AuthorReply)
        findings = list(stem_findings(artifact.stem))
        path = ticket_path(artifact.stem)
        if (self.checkout.repo / "tickets" / artifact.stem).exists():
            from chupa.artifacts import Finding
            findings.append(Finding(code=self.code, path=path, message=f"stem {artifact.stem!r} already exists",
                                    paved_road="choose a new, never-before-used ticket stem"))
        if any(event.ticket == artifact.stem for event in self.checkout.journal.read()):
            from chupa.artifacts import Finding
            findings.append(Finding(code=self.code, path=path, message=f"stem {artifact.stem!r} is already named in the journal",
                                    paved_road="choose a new, never-before-used ticket stem"))
        try:
            candidate = artifact.ticket
            if split_frontmatter(candidate) is not None:
                candidate = stamp(stamp(candidate, "source", f"box:{self.message_class}"), "state", "draft")
            validate_ticket(artifact.stem, candidate, self.checkout.repo)
        except TicketInvalid as exc:
            findings.extend(exc.findings)
        return GateReport(code=self.code, verdict="fail" if findings else "pass", findings=findings)


@dataclass(frozen=True)
class AuthorOutcome:
    stem: str | None = None
    decision: str | None = None


def _goal(text: str) -> str:
    after = text.partition("## Goal / Why\n")[2]
    return next((line.strip() for line in after.splitlines() if line.strip()), "")


async def _open_tickets(checkout: Checkout) -> str:
    states = {event.ticket: event.body.get("to") for event in checkout.journal.read()
              if event.type == EventType.STATE_TRANSITION and event.ticket is not None}
    lines = []
    for name in await checkout.git.ls_files(checkout.repo):
        path = Path(name)
        if len(path.parts) == 3 and path.parts[0] == "tickets" and path.name == "ticket.md":
            stem = path.parts[1]
            if states.get(stem) != "merged":
                lines.append(f"{stem}: {_goal((checkout.repo / path).read_text())}")
    return "\n".join(sorted(lines))


async def _commit_record(checkout: Checkout, driver: Driver, record_id: str) -> None:
    path = record_path(record_id)

    async def commit() -> None:
        await checkout.git.add(checkout.repo, [str(path)])
        await checkout.git.commit(checkout.repo, f"chupa(decisions): {record_id}", only=[str(path)])

    await driver.effects.run(commit, key=f"ticket-plane/decisions/{record_id}", ticket=None)


async def failure_decision(checkout: Checkout, driver: Driver, box: Box, message: Message, evidence: str) -> AuthorOutcome:
    record_id = f"decision-{message.id}"
    record = DecisionRecord(id=record_id, kind="decision", link=message.id, reopen_after_days=30)
    body = f"Author could not produce a ticket.\n\nEvidence: {evidence}\n"
    checkout.fs.write(checkout.repo / record_path(record_id), render_record(record, body).encode())
    await _commit_record(checkout, driver, record_id)
    box.resolve(message.id, Resolution(kind="decision", link=record_id))
    return AuthorOutcome(decision=record_id)


async def author(checkout: Checkout, driver: Driver, box: Box, message: Message, pass_no: int) -> AuthorOutcome:
    """Author and ticket-plane commit one recorded author verdict."""
    try:
        row = policy_row(message.message_class, message.bug_origin, message.has_repro)
    except ValueError as exc:
        return await failure_decision(checkout, driver, box, message, str(exc))
    assert message.verdict is not None
    spec: Spec = load_spec((SPECS_DIR / "author.md").read_text())
    files = "\n".join(await checkout.git.ls_files(checkout.repo))
    request = json.dumps({"class": message.message_class, "rationale": message.verdict.rationale,
                          "summary": message.summary})

    def render_author(_: object, findings: list) -> str:
        inputs = {"request": request, "files": files, "open_tickets": open_tickets,
                  "retry_findings": findings_text(findings)}
        return render(spec, inputs, spec.meta.effort)

    open_tickets = await _open_tickets(checkout)
    reviewed: RequisitionVerdict | None = None
    reviewed_text: str | None = None
    reviewed_state: str | None = None
    author_gate = AuthorGate(checkout, message.message_class)

    async def review_candidate(artifact: BaseModel, call_seq: int) -> GateReport:
        nonlocal reviewed, reviewed_text, reviewed_state
        assert isinstance(artifact, AuthorReply)
        if author_gate.check(artifact, checkout.repo).verdict == "fail":
            # Grammar-invalid candidates never spend a requisition review call.
            return GateReport(code="requisition_review", verdict="pass")
        provisional = stamp(stamp(artifact.ticket, "source", f"box:{message.message_class}"), "state", "draft")
        parsed = validate_ticket(artifact.stem, provisional, checkout.repo)
        state = start_state(checkout.config, row=row, fence=parsed.scope_fence,
                            gate_bypass=parsed.frontmatter.gate_bypass,
                            go=go_binds(checkout.journal.read(), baseline_identity(checkout.config, SPECS_DIR)))
        text = stamp(provisional, "state", state)
        reviewed = await review_ticket(
            driver, repo=checkout.repo, plan=(checkout.repo / "CHUPA_PLAN.md").read_text(),
            stem=artifact.stem, text=text, specs_dir=SPECS_DIR,
            tier=checkout.config.routing_default_tier, stem_slot="author", run_seq=pass_no,
            attempt=message.seq, call_seq=call_seq,
        )
        reviewed_text = text
        reviewed_state = state
        findings = reviewed.findings
        if reviewed.verdict == "rma":
            findings = [finding.model_copy(update={"code": "requisition_rma"}) for finding in findings]
        return GateReport(code="requisition_review", verdict="pass" if reviewed.verdict == "approve" else "fail",
                          findings=findings)

    checkout.journal.append(EventType.SIGNAL, {"signal": "author_invoked", "message": message.id})
    result = await driver.run(
        LlmStage(surface="author", emits=AuthorReply, gates=[author_gate],
                 render=render_author, review=review_candidate,
                 terminal_findings=frozenset({"requisition_rma"})), None,
        ticket=None, run_seq=pass_no, attempt=message.seq, workspace=checkout.repo,
        tier=checkout.config.routing_default_tier, effort=spec.meta.effort, stuck_budget=AUTHOR_STUCK_S,
    )
    if result.outcome != "ok" or not isinstance(result.artifact, AuthorReply):
        return await failure_decision(checkout, driver, box, message,
                                      findings_text(result.findings) or result.outcome)
    reply = result.artifact
    assert reviewed is not None and reviewed_text is not None and reviewed_state is not None
    text = reviewed_text
    path = ticket_path(reply.stem)
    checkout.fs.write(checkout.repo / path, text.encode())

    async def commit() -> str:
        await checkout.git.add(checkout.repo, [path])
        await checkout.git.commit(checkout.repo, f"chupa({reply.stem}): ticket", only=[path])
        return await checkout.git.rev_parse(checkout.repo, "HEAD")

    try:
        sha = await driver.effects.run(commit, key=f"ticket-plane/{reply.stem}/author", ticket=None)
    except Exception as exc:
        return await failure_decision(checkout, driver, box, message, f"commit failed: {type(exc).__name__}: {exc}")
    checkout.journal.append(EventType.SIGNAL, {"signal": "ticket_intake", "source": f"box:{message.message_class}",
                                                "state": reviewed_state,
                                                "new": True, "commit": sha}, ticket=reply.stem)
    checkout.journal.append(EventType.SIGNAL, {"signal": "requisition_verdict", "verdict": "approve",
                                                "ticket_sha": reviewed.ticket_sha, "provider": reviewed.provider,
                                                "model": reviewed.model, "spec_version": reviewed.spec_version},
                            ticket=reply.stem)
    box.resolve(message.id, Resolution(kind="ticket", link=reply.stem))
    return AuthorOutcome(stem=reply.stem)
