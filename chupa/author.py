"""The Suggestion Box Author stage (CHUPA_PLAN.md sections 12 and 13)."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from chupa.box import Box, BoxError, DecisionRecord, Message, Resolution, record_path, render_record
from chupa.driver import Driver, LlmStage, unwrap_fence
from chupa.gates import GateReport
from chupa.journal import EventType
from chupa.baseline import resolve_baseline
from chupa.policy import policy_row, start_state
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


def record_retro_ticket(journal, message: Message, stem: str) -> None:
    if message.message_class != "retro_finding":
        return
    body = {"kind": "retro_ticket_authored", "box_id": message.id,
            "retro_report_key": message.retro_report_key, "ticket_stem": stem}
    key = f"retro-ticket/{stem}"
    prior = [e for e in journal.read() if e.key == key or
             (e.body.get("kind") == "retro_ticket_authored" and
              (e.body.get("ticket_stem") == stem or e.body.get("box_id") == message.id))]
    if prior:
        if (len(prior) != 1 or prior[0].type != EventType.SIGNAL or prior[0].key != key
                or prior[0].ticket != stem or prior[0].body != body):
            raise BoxError("conflicting retro ticket provenance; restore the Author-produced bridge before resolving the Box")
        return
    journal.append(EventType.SIGNAL, body, ticket=stem, key=key)


async def recover_retro_ticket(checkout: Checkout, box: Box, message: Message) -> AuthorOutcome | None:
    """Finish the bridge/resolution crash window without another Author invocation."""
    if message.message_class != "retro_finding":
        return None
    history = checkout.journal.read()
    stems = set()
    for event in history:
        parts = (event.key or "").split("/")
        if (event.type != EventType.EFFECT_COMPLETION or len(parts) != 6
                or parts[:2] != ["llm", "author"] or parts[3:5] != ["author", str(message.seq)]):
            continue
        try:
            proposal = AuthorReply.model_validate_json(unwrap_fence(event.body["result"]["text"]))
        except ValueError:
            continue
        commit = next((e for e in history if e.type == EventType.EFFECT_COMPLETION
                       and e.key == f"ticket-plane/{proposal.stem}/author"), None)
        if commit is not None:
            text = await checkout.git._run(checkout.repo, "show",
                f"{commit.body['result']}:{ticket_path(proposal.stem)}")
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
        return await failure_decision(checkout, driver, box, message, str(exc))
    assert message.verdict is not None
    spec: Spec = load_spec((SPECS_DIR / "author.md").read_text())
    files = "\n".join(await checkout.git.ls_files(checkout.repo))
    request = json.dumps({"class": message.message_class, "rationale": message.verdict.rationale,
                          "summary": message.summary, "retro_report_key": message.retro_report_key,
                          "fixed_failure": message.fixed_failure,
                          "overcorrection_risk": message.overcorrection_risk,
                          "proposed_spec_paths": message.proposed_spec_paths, "reopen": message.reopen})

    def render_author(_: object, findings: list) -> str:
        inputs = {"request": request, "files": files, "open_tickets": open_tickets,
                  "retry_findings": findings_text(findings)}
        return render(spec, inputs)

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
                            go=resolve_baseline(checkout.config, checkout.journal.read(), specs_dir=SPECS_DIR).binds,
                            reopen=message.reopen)
        text = stamp(provisional, "state", state)
        reviewed = await review_ticket(
            driver, repo=checkout.repo, plan=(checkout.repo / "CHUPA_PLAN.md").read_text(),
            stem=artifact.stem, text=text, specs_dir=SPECS_DIR,
            tier=checkout.config.routing_default_tier, stem_slot="author", run_seq=pass_no,
            attempt=message.seq, call_seq=call_seq,
         expected_budget=AUTHOR_STUCK_S / 2)
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
        expected_budget='surface', scope_fence=())
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
    record_retro_ticket(checkout.journal, message, reply.stem)
    box.resolve(message.id, Resolution(kind="ticket", link=reply.stem))
    return AuthorOutcome(stem=reply.stem)
