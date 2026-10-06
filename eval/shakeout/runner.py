"""Fault-injection members for the production terminal handler."""

import json

from chupa.journal import EventType
from chupa.llm import HANG
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation
from eval.shakeout.stages import _commit, _configure_diagnosis, _finding, _ticket


def _diagnosis(verdict: str, lesson: str = "Follow the harvested finding.") -> str:
    return json.dumps({"verdict": verdict, "lessons": [lesson]})


def _terminals(bench: Bench, stem: str) -> list[dict]:
    return [event.body for event in bench.journal.read()
            if event.type == EventType.STATE_TRANSITION and event.ticket == stem
            and event.body.get("to") != "running"]


async def _commit_run_record(bench: Bench, stem: str, marker: str) -> None:
    path = bench.repo / "tickets" / stem / "run.md"
    bench.fs.write(path, f"## Dead ends\n\n- {marker}\n".encode())
    paths = [f"tickets/{stem}/ticket.md", f"tickets/{stem}/run.md"]
    await bench.git.add(bench.repo, paths)
    await bench.git.commit(bench.repo, f"shakeout({stem}): run record", only=paths)


async def _premise_false(bench: Bench) -> Observation:
    stem = "premise-false"
    bench.add_ticket(stem, _ticket(stem, "premise.txt", "true"))
    _configure_diagnosis(bench)
    finding = {"code": "premise", "message": "fixture premise is false",
               "paved_road": "correct the fixture premise"}
    bench.script([json.dumps({"outcome": "premise_failed", "summary": "premise", "surprises": "none",
                              "dead_ends": "none", "predicted_vs_actual": "10m predicted, 1m actual",
                              "findings": [finding]}), _diagnosis("retry")])
    await bench.drain()

    terminal, = _terminals(bench, stem)
    bounces = [event for event in bench.journal.read()
               if event.type == EventType.CAP_CONSUMED and event.ticket == stem
               and event.body.get("cap") == "premise_bounce"]
    retries = [event for event in bench.journal.read()
               if event.type == EventType.CAP_CONSUMED and event.ticket == stem
               and event.body.get("cap") == "retry"]
    harvested = _finding(bench, stem, "premise")
    implements = [request for request in bench.llm.requests if request.surface == "implement"]
    assert terminal["to"] == "premise_failed" and terminal["stage"] == "implement"
    assert len(bounces) == 1 and not retries and len(implements) == 1
    assert harvested.message == finding["message"]
    return Observation("premise_harvested_without_reoffer", f"{stem}/0")


async def _timeout_dead_ends(bench: Bench) -> Observation:
    stem = "timeout-dead-ends"
    marker = "unique-dead-end-marker"
    bench.add_ticket(stem, _ticket(stem, "timeout.txt", "test -f timeout.txt"))
    await _commit_run_record(bench, stem, marker)
    _configure_diagnosis(bench)
    lesson = f"Address {marker} before retrying."
    bench.script([lambda _req: (bench.advance_sleep(), HANG)[1], _diagnosis("retry", lesson),
                  lambda req: _commit(req, {"timeout.txt": "ok\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    report = await bench.drain()

    prompts = [request.rendered for request in bench.llm.requests if request.surface == "implement"]
    diagnosis = next(event.body for event in bench.journal.read()
                     if event.type == EventType.SIGNAL and event.ticket == stem
                     and event.body.get("signal") == "diagnosis")
    assert len(prompts) == 2 and "`timeout`" in prompts[1] and lesson in prompts[1]
    assert diagnosis["lessons"] == [lesson] and stem in report.merged
    return Observation("timeout_lesson_rendered_on_retry", f"{stem}/1")


async def _identical_terminals(bench: Bench) -> Observation:
    stem = "identical-terminals"
    bench.add_ticket(stem, _ticket(stem, "identical.txt", "test -f identical.txt"))
    _configure_diagnosis(bench)
    bench.configure(bench.config.model_copy(update={
        "caps": bench.config.caps.model_copy(update={"retry": 3, "diagnosis": 4}),
    }))
    snag = {"code": "logic", "path": "identical.txt", "line": 1, "message": "same wall",
            "paved_road": "repair the same wall"}
    fail = lambda req: _commit(req, {"identical.txt": "still blocked\n"})
    verdict = json.dumps({"verdict": "snag", "summary": "snag", "findings": [snag]})
    bench.script([fail, verdict, _diagnosis("retry"), fail, verdict, _diagnosis("retry"),
                  fail, verdict, _diagnosis("retry"),
                  lambda req: _commit(req, {"identical.txt": "fixed\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    report = await bench.drain()

    terminals = _terminals(bench, stem)
    assert [terminal["reason"] for terminal in terminals[:3]] == ["logic"] * 3
    assert terminals[2]["dispatch"] == "escalate" and "rung" in terminals[2]
    assert stem in report.merged
    return Observation("identical_reason_escalates_at_k", f"{stem}/3")


MEMBERS = (
    Member("premise_false", "runner", "Implement replies premise_failed", "premise_harvested_without_reoffer",
           _premise_false),
    Member("timeout_dead_ends", "runner", "Implement hangs after a marked run record",
           "timeout_lesson_rendered_on_retry", _timeout_dead_ends),
    Member("identical_terminals", "runner", "Review repeats one finding code",
           "identical_reason_escalates_at_k", _identical_terminals),
)
