"""One operator-triggered, sequential Suggestion Box pass (plan section 12)."""

import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from chupa.box import BOX_DIR, Box, DecisionRecord, Resolution, Verdict, read_registry, record_path, render_record
from chupa.author import author, failure_decision
from chupa.driver import Driver, LlmStage
from chupa.git import GitError
from chupa.journal import EventType
from chupa.llm import LLM
from chupa.runner import Checkout, SPECS_DIR
from chupa.specs import load_spec, render
from chupa.stages import findings_text
from chupa.status import last_states

TRIAGE_STUCK_S = 600.0
NonBlank = Annotated[str, Field(min_length=1, pattern=r"\S")]


class TriageReply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    verdict: Literal["author", "tombstone", "decision"]
    link: str | None
    summary: NonBlank
    rationale: NonBlank
    evidence: list[str]
    reopen_after_days: Annotated[int, Field(ge=1)] | None

    @model_validator(mode="after")
    def _coherent(self) -> "TriageReply":
        if (self.link is not None) != (self.verdict == "tombstone"):
            raise ValueError("link is required exactly for tombstone")
        if self.verdict == "tombstone" and not self.link.strip():
            raise ValueError("tombstone link must not be blank")
        if (self.reopen_after_days is not None) != (self.verdict != "author"):
            raise ValueError("reopen_after_days is required exactly for tombstone and decision")
        return self


async def _committed(checkout: Checkout, path: Path) -> bool:
    try:
        await checkout.git.rev_parse(checkout.repo, f"HEAD:{path}")
    except GitError:
        return False
    return True


async def _commit_record(checkout: Checkout, driver: Driver, record_id: str) -> None:
    path = record_path(record_id)

    async def commit() -> None:
        await checkout.git.add(checkout.repo, [str(path)])
        await checkout.git.commit(checkout.repo, f"chupa(decisions): {record_id}", only=[str(path)])

    await driver.effects.run(commit, key=f"ticket-plane/decisions/{record_id}", ticket=None)


def _body(reply: TriageReply, message_id: str, raw_summary: str) -> str:
    lines = [reply.summary, "", reply.rationale, ""]
    lines.extend(f"- {item}" for item in reply.evidence)
    lines.extend(["", f"Message: {message_id}", ""])
    return "\n".join(lines).replace(raw_summary, "[message summary omitted]")


async def _record(
    checkout: Checkout, driver: Driver, box: Box, message_id: str,
    kind: Literal["decision", "tombstone"], link: str, reply: TriageReply, raw_summary: str,
) -> str:
    record_id = f"{kind}-{message_id}"
    assert reply.reopen_after_days is not None
    record = DecisionRecord(id=record_id, kind=kind, link=link,
                            reopen_after_days=reply.reopen_after_days)
    checkout.fs.write(checkout.repo / record_path(record_id),
                      render_record(record, _body(reply, message_id, raw_summary)).encode())
    await _commit_record(checkout, driver, record_id)
    box.resolve(message_id, Resolution(kind=kind, link=record_id))
    return f"{message_id}: {kind} -> {record_id}"


def _goal(text: str) -> str:
    after = text.partition("## Goal / Why\n")[2]
    return next((line.strip() for line in after.splitlines() if line.strip()), "")


async def triage_pass(checkout: Checkout, llm: LLM) -> list[tuple[str, str]]:
    """Journal one pass, then settle each pending message in sequence order."""
    history = checkout.journal.read()
    pass_no = sum(e.type == EventType.SIGNAL and e.body.get("signal") == "triage_pass" for e in history)
    checkout.journal.append(EventType.SIGNAL, {"signal": "triage_pass", "pass": pass_no})
    box = Box(checkout.config.state_dir / BOX_DIR, checkout.fs)
    spec = load_spec((SPECS_DIR / "triage.md").read_text())
    driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock,
                                sleep=checkout.sleep, fs=checkout.fs)
    states = last_states(history)
    merged = sorted(stem for stem, state in states.items() if state == "merged")
    lines: list[tuple[str, str]] = []
    for message in box.pending():
        registry = read_registry(checkout.repo)
        existing = next((r for r, _ in registry if r.id in
                         {f"decision-{message.id}", f"tombstone-{message.id}"}), None)
        if existing is not None:
            if not await _committed(checkout, record_path(existing.id)):
                await _commit_record(checkout, driver, existing.id)
            box.resolve(message.id, Resolution(kind=existing.kind, link=existing.id))
            lines.append((message.id, f"{message.id}: {existing.kind} -> {existing.id}"))
            continue

        if message.verdict is not None and message.verdict.verdict == "author":
            if message.verdict.produced_by_spec_version != spec.meta.version:
                reply = TriageReply(
                    verdict="decision", link=None, summary="Recorded author verdict superseded",
                    rationale="The triage policy changed before the Author stage handled this message.",
                    evidence=[f"recorded version: {message.verdict.produced_by_spec_version}",
                              f"current version: {spec.meta.version}"], reopen_after_days=30,
                )
                line = await _record(checkout, driver, box, message.id, "decision", message.id, reply,
                                     message.summary)
            else:
                invoked = any(event.type == EventType.SIGNAL and event.body.get("signal") == "author_invoked"
                              and event.body.get("message") == message.id for event in checkout.journal.read())
                outcome = (await failure_decision(checkout, driver, box, message, "previous Author invocation did not settle")
                           if invoked else await author(checkout, driver, box, message, pass_no))
                line = f"{message.id}: " + (f"ticket -> {outcome.stem}" if outcome.stem else f"decision -> {outcome.decision}")
            lines.append((message.id, line))
            continue

        open_tickets = []
        for path in sorted((checkout.repo / "tickets").glob("*/ticket.md")):
            stem = path.parent.name
            if stem not in merged and await _committed(checkout, path.relative_to(checkout.repo)):
                open_tickets.append(f"{stem}: {_goal(path.read_text())}")
        inputs = {
            "message": json.dumps({"class": message.message_class, "summary": message.summary,
                                   "origin": message.origin, "stage": message.stage,
                                   "outcome": message.outcome}),
            "open_tickets": "\n".join(open_tickets),
            "merged": "\n".join(merged),
            "decisions": "\n".join(f"{r.id}: {r.kind}, link={r.link}, {body.splitlines()[0] if body else ''}"
                                     for r, body in registry),
        }

        def render_message(_consumed: object, findings: list) -> str:
            return render(spec, {**inputs, "retry_findings": findings_text(findings)})

        result = await driver.run(
            LlmStage(surface="triage", emits=TriageReply, gates=[], render=render_message), message,
            ticket=None, run_seq=message.seq, attempt=pass_no, workspace=checkout.repo,
            tier=checkout.config.routing_default_tier, effort=spec.meta.effort, stuck_budget=TRIAGE_STUCK_S,
        )
        if result.outcome != "ok":
            line = f"{message.id}: {result.outcome}; remains pending"
        else:
            reply = result.artifact
            assert isinstance(reply, TriageReply)
            if reply.verdict == "author":
                box.record_verdict(message.id, Verdict(verdict="author", produced_by_spec_version=spec.meta.version,
                                                      rationale=reply.rationale))
                outcome = await author(checkout, driver, box, box.get(message.id), pass_no)
                line = f"{message.id}: " + (f"ticket -> {outcome.stem}" if outcome.stem else f"decision -> {outcome.decision}")
            else:
                kind = reply.verdict
                if kind == "tombstone":
                    assert reply.link is not None
                    target = (reply.link in merged or
                              await _committed(checkout, Path("tickets") / reply.link / "ticket.md"))
                    if not target:
                        for record, _ in registry:
                            if record.id == reply.link and await _committed(checkout, record_path(record.id)):
                                target = True
                                break
                    if not target:
                        reply = reply.model_copy(update={
                            "verdict": "decision", "link": None,
                            "evidence": [*reply.evidence, f"unresolvable link: {reply.link}"],
                        })
                        kind = "decision"
                line = await _record(checkout, driver, box, message.id, kind,
                                     reply.link if kind == "tombstone" else message.id, reply,
                                     message.summary)
        lines.append((message.id, line))
    return lines
