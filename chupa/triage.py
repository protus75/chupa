"""One operator-triggered, sequential Suggestion Box pass."""

import json
import re
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from chupa.author import author, commit_record, committed, failure_declined, list_open_tickets, recover_retro_ticket
from chupa.box import BOX_DIR, Box, DecisionRecord, RereportJournal, Resolution, Verdict, read_registry, record_path, render_record
from chupa.driver import Driver, LlmStage
from chupa.effects import Effects
from chupa.git import GitError
from chupa.inbox import ingest, report_data
from chupa.journal import EventType
from chupa.llm import LLM
from chupa.runner import SPECS_DIR, Checkout
from chupa.seams import ExecutableNotFound
from chupa.specs import load_spec, render
from chupa.stages import findings_text
from chupa.status import last_states

TRIAGE_STUCK_S = 600.0
ESCAPE_ATTRIBUTION = "escape-attribution"
NonBlank = Annotated[str, Field(min_length=1, pattern=r"\S")]


class TriageReply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    verdict: Literal["author", "tombstone", "declined"]
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
            raise ValueError("reopen_after_days is required exactly for tombstone and declined")
        return self


def _body(reply: TriageReply, message_id: str, raw_summary: str) -> str:
    lines = [reply.summary, "", reply.rationale, ""]
    lines.extend(f"- {item}" for item in reply.evidence)
    lines.extend(["", f"Message: {message_id}", ""])
    return "\n".join(lines).replace(raw_summary, "[message summary omitted]")


async def _record(
    checkout: Checkout,
    driver: Driver,
    box: Box,
    message_id: str,
    kind: Literal["declined", "tombstone"],
    link: str,
    reply: TriageReply,
    raw_summary: str,
) -> str:
    record_id = f"{kind}-{message_id}"
    assert reply.reopen_after_days is not None
    record = DecisionRecord(id=record_id, kind=kind, link=link, reopen_after_days=reply.reopen_after_days)
    checkout.fs.write(checkout.repo / record_path(record_id), render_record(record, _body(reply, message_id, raw_summary)).encode())
    await commit_record(checkout, driver, record_id)
    box.resolve(message_id, Resolution(kind=kind, link=record_id))
    return f"{message_id}: {kind} -> {record_id}"


async def triage_pass(checkout: Checkout, llm: LLM, ids=frozenset()) -> list[tuple[str, str]]:
    """Journal one pass, then settle each pending message in sequence order."""
    validate_ids(checkout, ids)
    history = checkout.journal.read()
    pass_no = sum(e.type == EventType.SIGNAL and e.body.get("signal") == "triage_pass" for e in history)
    checkout.journal.append(EventType.SIGNAL, {"signal": "triage_pass", "pass": pass_no})
    box = report_intake(checkout)
    spec = load_spec((SPECS_DIR / "triage.md").read_text())
    driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
    driver.journal = checkout.journal
    driver.effects = Effects(checkout.journal)
    lines = await _settle_pass(checkout, driver, box, spec, history, pass_no, ids)
    for message in box.messages():
        if message.message_class == "bug_report" and message.resolution is not None and message.resolution.kind == "ticket":
            try:
                await attribute_escape(checkout, driver, message)
            except (GitError, OSError, ExecutableNotFound, ValueError, KeyError, yaml.YAMLError) as exc:
                driver.log.event("escape_attribution_incomplete", box_id=message.id, error=str(exc), paved_road="repair repository/evidence access and retry triage")
                lines.append((message.id, f"{message.id}: attribution incomplete; repair repository/evidence access and retry triage"))
    return lines


def validate_ids(checkout: Checkout, ids):
    box = Box(checkout.config.state_dir / BOX_DIR, checkout.fs, rereport=RereportJournal(checkout.journal))
    for id in ids:
        box.get(id)
    return box


async def dismiss(checkout: Checkout, ids) -> list[str]:
    box = validate_ids(checkout, ids)
    driver = Driver.from_config(checkout.config, llm=None, env=checkout.env, clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
    driver.journal = checkout.journal
    driver.effects = Effects(checkout.journal)
    lines = []
    for id in ids:
        message = box.get(id)
        if message.resolution is not None:
            lines.append(f"{id}: already resolved -> {message.resolution.link}")
            continue
        reply = TriageReply(verdict="declined", link=None, summary="Dismissed by the operator.", rationale="The operator dismissed this message.", evidence=[], reopen_after_days=30)
        lines.append(await _record(checkout, driver, box, id, "declined", id, reply, message.summary))
    return lines


async def _passed_surfaces(checkout, candidate, history):
    """Pin Check and Review to the completed admission, including clean-rebase carry."""
    from chupa.artifacts import ReviewVerdict
    from chupa.driver import unwrap_fence
    from chupa.stages import ApprovedInvoice, Invoice, read_review

    stem, sha = candidate["ticket"], candidate["reviewed_sha"]
    admission = next(
        (
            i
            for i, e in enumerate(history)
            if e.type == EventType.EFFECT_COMPLETION
            and e.ticket == stem
            and re.fullmatch(rf"merge/{re.escape(stem)}/[0-9]+", e.key or "")
            and e.body.get("result", {}).get("commit") == candidate["commit"]
        ),
        None,
    )
    if admission is None:
        return []
    before = history[:admission]
    attempt = history[admission].key.split("/")[-1]
    surfaces = set()
    for kind in ("checks", "review"):
        key = f"ticket-plane/{stem}/{attempt}/{kind}"
        lift = next((e for e in reversed(before) if e.type == EventType.EFFECT_COMPLETION and e.ticket == stem and e.key == key), None)
        if lift is None:
            continue
        commit = lift.body["result"]["commit"]
        if re.fullmatch(r"[0-9a-f]{40}", commit) is None:
            raise ValueError("invalid completed evidence commit")
        if await checkout.git.merge_base(checkout.repo, commit, candidate["commit"]) != commit:
            continue
        path = f"tickets/{stem}/" + ("checks.json" if kind == "checks" else "review.md")
        text = await checkout.git._run(checkout.repo, "show", f"{commit}:{path}")
        if kind == "checks":
            invoice = Invoice.model_validate_json(text)
            if invoice.stem == stem and invoice.produced_at_sha == sha and invoice.passed:
                surfaces.update(r.code for r in invoice.reports if r.verdict == "pass" and r.code not in invoice.bypassed)
        else:
            review = read_review(text)
            if not isinstance(review, ApprovedInvoice) or review.stem != stem or review.reviewed_sha != sha or review.produced_at_sha != sha:
                continue
            calls = [
                e
                for e in before[: before.index(lift)]
                if e.type == EventType.EFFECT_COMPLETION and e.ticket == stem and re.fullmatch(rf"llm/{re.escape(stem)}/[0-9]+/review/{attempt}/[0-9]+", e.key or "")
            ]
            if calls:
                verdict = ReviewVerdict.model_validate_json(unwrap_fence(calls[-1].body["result"]["text"]))
                if verdict.verdict == "approve":
                    surfaces.add("review")
    return sorted(surfaces)


async def attribute_escape(checkout, driver, message):
    """Effects snapshots resolved report attribution once per durable Box identity."""
    from chupa.tickets import Frontmatter, split_frontmatter

    stem = message.resolution.link

    async def collect():
        history = checkout.journal.read()
        result = {
            "box_id": message.id,
            "bug_ticket": stem,
            "app_commit": message.report.report.app_commit if message.report else None,
            "matches": [],
            "confidence_note": "Attribution unavailable: missing authored bug/report evidence.",
        }
        authored = next((e for e in history if e.type == EventType.EFFECT_COMPLETION and e.key == f"ticket-plane/{stem}/author"), None)
        if authored is None:
            return result
        commit = authored.body["result"]
        if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
            raise ValueError("invalid authored ticket commit")
        text = await checkout.git._run(checkout.repo, "show", f"{commit}:tickets/{stem}/ticket.md")
        front = split_frontmatter(text)
        if front is None:
            raise ValueError("authored ticket has no frontmatter; restore its committed evidence")
        # Author already validated the committed ticket; current plan/graph changes
        # cannot invalidate this historical origin evidence.
        fields = Frontmatter.model_validate(yaml.safe_load(front[0]))
        if fields.kind != "bug" or fields.source != "box:bug_report" or message.report is None:
            return result
        report = message.report.report
        candidates = await checkout.git.first_parent_squashes(checkout.repo, report.app_commit)
        for candidate in candidates:
            if report.implicated_paths and not set(candidate["paths"]).intersection(report.implicated_paths):
                continue
            surfaces = await _passed_surfaces(checkout, candidate, history)
            if surfaces:
                result["matches"].append({k: candidate[k] for k in ("ticket", "commit", "reviewed_sha")} | {"surfaces": surfaces})
        if result["matches"]:
            result["confidence_note"] = ("Bounded-range" if ".." in report.app_commit else "Single-commit") + (
                " candidate evidence" + (", narrowed by implicated paths" if report.implicated_paths else ", without path narrowing") + "; exact introducing commit is unproven."
            )
        else:
            result["confidence_note"] = "Attribution unavailable: no first-parent candidates with matching paths and proven passed admission surfaces."
        return result

    return await driver.effects.run(collect, key=f"{ESCAPE_ATTRIBUTION}/{message.id}", ticket=stem)


async def _settle_pass(checkout, driver, box, spec, history, pass_no, ids):
    states = last_states(history)
    merged = sorted(stem for stem, state in states.items() if state == "merged")
    lines: list[tuple[str, str]] = []
    for message in box.pending():
        if ids and message.id not in ids:
            continue
        if recovered := await recover_retro_ticket(checkout, box, message):
            lines.append((message.id, f"{message.id}: ticket -> {recovered.stem}"))
            continue
        registry = read_registry(checkout.repo)
        if message.reopen:
            registry = [(r, body) for r, body in registry if r.id != f"tombstone-{message.id}"]
        existing = next((r for r, _ in registry if r.id in {f"declined-{message.id}", f"tombstone-{message.id}"}), None)
        if existing is not None:
            if not await committed(checkout, record_path(existing.id)):
                await commit_record(checkout, driver, existing.id)
            box.resolve(message.id, Resolution(kind=existing.kind, link=existing.id))
            lines.append((message.id, f"{message.id}: {existing.kind} -> {existing.id}"))
            continue

        if message.verdict is not None and message.verdict.verdict == "author":
            if message.verdict.produced_by_spec_version != spec.meta.version:
                reply = TriageReply(
                    verdict="declined",
                    link=None,
                    summary="Recorded author verdict superseded",
                    rationale="The triage policy changed before the Author stage handled this message.",
                    evidence=[f"recorded version: {message.verdict.produced_by_spec_version}", f"current version: {spec.meta.version}"],
                    reopen_after_days=30,
                )
                line = await _record(checkout, driver, box, message.id, "declined", message.id, reply, message.summary)
            else:
                journal = checkout.journal.read()
                boundary = max(
                    (
                        i
                        for i, event in enumerate(journal)
                        if event.type == EventType.EFFECT_INTENT and (event.key or "").startswith(f"retro-recurrence/{message.id}/") and event.body.get("reopened") is True
                    ),
                    default=-1,
                )
                invoked = any(event.type == EventType.SIGNAL and event.body.get("signal") == "author_invoked" and event.body.get("message") == message.id for event in journal[boundary + 1 :])
                outcome = await failure_declined(checkout, driver, box, message, "previous Author invocation did not settle") if invoked else await author(checkout, driver, box, message, pass_no)
                line = f"{message.id}: " + (f"ticket -> {outcome.stem}" if outcome.stem else f"declined -> {outcome.declined}")
            lines.append((message.id, line))
            continue

        open_tickets = await list_open_tickets(checkout)
        inputs = {
            "message": json.dumps(
                {
                    "class": message.message_class,
                    "summary": message.summary,
                    "origin": message.origin,
                    "stage": message.stage,
                    "outcome": message.outcome,
                    "retro_report_key": message.retro_report_key,
                    "fixed_failure": message.fixed_failure,
                    "overcorrection_risk": message.overcorrection_risk,
                    "proposed_spec_paths": [f"chupa/{path}" for path in message.proposed_spec_paths],
                    "test_issue": message.test_issue,
                    "proposed_paths": message.proposed_paths,
                    "reopen": message.reopen,
                    "report": report_data(message.report, box.root) if message.report else None,
                }
            ),
            "open_tickets": open_tickets,
            "merged": "\n".join(merged),
            "decisions": "\n".join(f"{r.id}: {r.kind}, link={r.link}, {body.splitlines()[0] if body else ''}" for r, body in registry),
        }

        def render_message(_consumed: object, findings: list) -> str:
            return render(spec, {**inputs, "retry_findings": findings_text(findings)})

        result = await driver.run(
            LlmStage(surface="triage", emits=TriageReply, gates=[], render=render_message),
            message,
            ticket=None,
            run_seq=message.seq,
            attempt=pass_no,
            workspace=checkout.repo,
            tier=checkout.config.routing_default_tier,
            effort=spec.meta.effort,
            stuck_budget=TRIAGE_STUCK_S,
            expected_budget="surface",
            scope_fence=(),
        )
        if result.outcome != "ok":
            line = f"{message.id}: {result.outcome}; remains pending"
        else:
            reply = result.artifact
            assert isinstance(reply, TriageReply)
            # Every tombstone verdict would reuse the committed record's id, even
            # when it names another link. Reopening preserves that record's bytes.
            if message.reopen and reply.verdict == "tombstone":
                reply = reply.model_copy(update={"verdict": "author", "link": None, "reopen_after_days": None})
            if reply.verdict == "author":
                box.record_verdict(message.id, Verdict(verdict="author", produced_by_spec_version=spec.meta.version, rationale=reply.rationale))
                outcome = await author(checkout, driver, box, box.get(message.id), pass_no)
                line = f"{message.id}: " + (f"ticket -> {outcome.stem}" if outcome.stem else f"declined -> {outcome.declined}")
            else:
                kind = reply.verdict
                if kind == "tombstone":
                    assert reply.link is not None
                    target = reply.link in merged or await committed(checkout, Path("tickets") / reply.link / "ticket.md")
                    if not target:
                        for record, _ in registry:
                            if record.id == reply.link and await committed(checkout, record_path(record.id)):
                                target = True
                                break
                    if not target:
                        reply = reply.model_copy(
                            update={
                                "verdict": "declined",
                                "link": None,
                                "evidence": [*reply.evidence, f"unresolvable link: {reply.link}"],
                            }
                        )
                        kind = "declined"
                    else:
                        for prior in box.messages():
                            if prior.id != message.id and prior.resolution is not None and prior.resolution.kind == "tombstone" and prior.resolution.link == reply.link:
                                box.record_rereport(prior.id, occurrence_id=f"semantic/{message.id}")
                line = await _record(checkout, driver, box, message.id, kind, reply.link if kind == "tombstone" else message.id, reply, message.summary)
        lines.append((message.id, line))
    return lines


def report_intake(checkout: Checkout) -> Box:
    from chupa.enginelog import EngineLog
    from chupa.redact import Redactor

    if checkout.config.report_inbox is None:
        box = Box(checkout.config.state_dir / BOX_DIR, checkout.fs, rereport=RereportJournal(checkout.journal))
    else:
        from chupa.daemon import storm_producer

        box = storm_producer(root=checkout.config.state_dir / BOX_DIR, fs=checkout.fs, journal=checkout.journal, clock=checkout.clock)
        box.recover()
    log = EngineLog(checkout.config.state_dir / "engine.log", Redactor.from_config(checkout.config, checkout.env), checkout.clock)
    if checkout.config.report_inbox is not None:
        ingest(box, root=checkout.repo, inbox=checkout.config.report_inbox, diagnostic=lambda error: log.event("report_intake_refused", error=error))
    drops = checkout.config.state_dir / BOX_DIR / "suggestions"
    for path in sorted(drops.glob("*.json")):
        try:
            data = json.loads(path.read_bytes())
            if not isinstance(data, dict) or set(data) != {"summary"} or not isinstance(data["summary"], str) or not data["summary"].strip():
                raise ValueError("expected an object with one nonblank string summary")
        except (OSError, ValueError, UnicodeError) as exc:
            log.event("suggestion_intake_refused", error=f"{path.name}: {exc}; repair this arrival and retry triage")
            continue
        box.enqueue(message_class="suggestion", origin="session", summary=data["summary"], occurrence_id=path.stem)
        consumed = drops / "consumed"
        consumed.mkdir(parents=True, exist_ok=True)
        checkout.fs.replace(path, consumed / path.name)
    return box
