"""Fault-injection members for the shared LLM-stage driver."""

import json

from chupa.journal import EventType
from chupa.llm import HANG
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation
from eval.shakeout.stages import _commit, _configure_diagnosis, _finding, _ticket


def _diagnosis(verdict: str) -> str:
    return json.dumps({"verdict": verdict, "lessons": ["Follow the harvested finding."]})


def _diagnosis_signal(bench: Bench, stem: str) -> dict:
    return next(event.body for event in reversed(_first_attempt_events(bench, stem))
                if event.type == EventType.SIGNAL and event.ticket == stem
                and event.body.get("signal") == "diagnosis")


async def _invalid_output_exhausted(bench: Bench) -> Observation:
    stem = "invalid-output-exhausted"
    next_stem = "valid-after-invalid"
    bench.add_ticket(stem, _ticket(stem, "invalid.txt", "true"))
    bench.add_ticket(next_stem, _ticket(next_stem, "valid.txt", "test -f valid.txt"))
    _configure_diagnosis(bench)
    bench.script([
        "not JSON",
        '{"outcome": "not-a-valid-outcome"}',
        _diagnosis("reject"),
        lambda req: _commit(req, {"valid.txt": "ok\n"}),
        json.dumps({"verdict": "approve", "summary": "approved", "findings": []}),
    ])
    report = await bench.drain()

    diagnosis_at = next(index for index, request in enumerate(bench.llm.requests)
                        if request.ticket == stem and request.surface == "diagnose")
    requests = [request for request in bench.llm.requests[:diagnosis_at]
                if request.ticket == stem and request.surface == "implement"]
    assert len(requests) == bench.config.caps.retry + 1
    assert all("invalid_artifact" in request.rendered for request in requests[1:]), [
        request.rendered for request in requests[1:]
    ]
    terminal = _terminals(bench, stem)[0]
    finding = _finding(bench, stem, "invalid_artifact")
    diagnosis = _diagnosis_signal(bench, stem)
    assert terminal["to"] == "invalid_artifact" and terminal["stage"] == "implement"
    assert finding.code == "invalid_artifact"
    assert diagnosis["verdict"] == "reject" and diagnosis["mechanical"] is None
    assert next_stem in report.merged
    return Observation("invalid_artifact_harvested_after_bounded_reprompts", f"{stem}/0")


async def _stuck_budget_kill(bench: Bench) -> Observation:
    stem = "stuck-budget-kill"
    next_stem = "stuck-followup"
    bench.add_ticket(stem, _ticket(stem, "stuck.txt", "true"))
    bench.add_ticket(next_stem, _ticket(next_stem, "followup.txt", "test -f followup.txt"))
    _configure_diagnosis(bench)
    bench.script([
        lambda _req: (bench.advance_sleep(), HANG)[1],
        _diagnosis("reject"),
        lambda req: _commit(req, {"followup.txt": "ok\n"}),
        json.dumps({"verdict": "approve", "summary": "approved", "findings": []}),
    ])
    report = await bench.drain()

    terminal = _terminals(bench, stem)[0]
    harvest = json.loads((bench.repo / "tickets" / stem / "attempts" / "0" / "harvest.json").read_text())
    infra = [event for event in _first_attempt_events(bench, stem)
             if event.type == EventType.CAP_CONSUMED and event.ticket == stem
             and event.body.get("cap") == "infra"]
    assert bench.llm.aborted == 1
    assert bench.clock.now.year == 2026 and bench.clock.now.minute == 20, bench.clock.now
    assert terminal["to"] == "timeout" and terminal["stage"] == "implement"
    assert len(infra) == 1 and harvest["reason"] == "timeout"
    assert next_stem in report.merged
    return Observation("timeout_harvest_reason_after_stuck_kill", f"{stem}/0")


def _terminals(bench: Bench, stem: str) -> list[dict]:
    return [event.body for event in bench.journal.read()
            if event.type == EventType.STATE_TRANSITION and event.ticket == stem
            and event.body.get("to") != "running"]


def _first_attempt_events(bench: Bench, stem: str):
    events = bench.journal.read()
    terminal_at = next(index for index, event in enumerate(events)
                       if event.type == EventType.STATE_TRANSITION and event.ticket == stem
                       and event.body.get("to") != "running")
    return events[:terminal_at + 1]


MEMBERS = (
    Member("invalid_output_exhausted", "driver", "unparseable Implement replies exhaust re-prompts",
           "invalid_artifact_harvested_after_bounded_reprompts", _invalid_output_exhausted),
    Member("stuck_budget_kill", "driver", "Implement hangs past its stuck budget",
           "timeout_harvest_reason_after_stuck_kill", _stuck_budget_kill),
)
