"""Fault-injection members for the production drain."""

import json

from chupa.caps import draws
from chupa.journal import EventType
from chupa.stages import read_review
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation
from eval.shakeout.stages import _commit, _configure_diagnosis, _ticket


async def _commit_tickets(bench: Bench, paths: list[str], message: str) -> None:
    await bench.git.add(bench.repo, paths)
    await bench.git.commit(bench.repo, message, only=paths)


def _terminals(bench: Bench, stem: str) -> list[dict]:
    return [event.body for event in bench.journal.read()
            if event.type == EventType.STATE_TRANSITION and event.ticket == stem
            and event.body.get("to") != "running"]


async def _bad_schema(bench: Bench) -> Observation:
    invalid, valid = "bad-schema", "valid-schema"
    await bench.initialize()
    bench.add_ticket(invalid, "---\nstate: confirmed\nsource: human\npriority: P2\nkind: feature\n---\n")
    bench.add_ticket(valid, _ticket(valid, "valid.txt", "test -f valid.txt"))
    await _commit_tickets(bench, [f"tickets/{invalid}/ticket.md", f"tickets/{valid}/ticket.md"],
                          "shakeout: committed schema fixtures")
    bench.script([lambda req: _commit(req, {"valid.txt": "ok\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    report = await bench.drain()

    invalid_events = [event for event in bench.journal.read() if event.ticket == invalid]
    assert not invalid_events
    assert all(request.ticket != invalid for request in bench.llm.requests)
    assert valid in report.merged
    assert len(report.invalid) == 1 and report.invalid[0][0] == invalid
    assert report.invalid[0][1]
    assert f"{invalid}:" in report.render()
    return Observation("invalid_committed_ticket_reported_without_dispatch", f"{valid}/0")


async def _premise_park_release(bench: Bench) -> Observation:
    stem = "premise-park-release"
    bench.add_ticket(stem, _ticket(stem, "premise.txt", "test -f premise.txt"))
    _configure_diagnosis(bench)
    finding = {"code": "premise", "message": "fixture premise is false",
               "paved_road": "correct the fixture premise"}
    bench.script([json.dumps({"outcome": "premise_failed", "summary": "premise", "surprises": "none",
                              "dead_ends": "none", "predicted_vs_actual": "10m predicted, 1m actual",
                              "findings": [finding]}),
                  json.dumps({"verdict": "retry", "lessons": ["Fix the fixture premise."]})])
    first = await bench.drain()
    requests_after_first = len(bench.llm.requests)
    second = await bench.drain()
    assert len(bench.llm.requests) == requests_after_first
    assert stem not in first.merged and stem not in second.merged
    assert "parked until its committed ticket.md changes" in second.render()
    assert f"editing tickets/{stem}/ticket.md" in second.render()

    path = bench.repo / "tickets" / stem / "ticket.md"
    path.write_text(path.read_text().replace("Exercise the stage fixture", "Correct the stage fixture"))
    await _commit_tickets(bench, [f"tickets/{stem}/ticket.md"], "shakeout: correct premise fixture")
    bench.script([lambda req: _commit(req, {"premise.txt": "ok\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    released = await bench.drain()

    assert stem in released.merged
    assert [terminal["to"] for terminal in _terminals(bench, stem)] == ["premise_failed", "merged"]
    return Observation("unchanged_premise_is_parked_then_content_change_releases", f"{stem}/1")


async def _red_then_green(bench: Bench) -> Observation:
    stem = "red-then-green"
    message = "first review finding"
    bench.add_ticket(stem, _ticket(stem, "retry.txt", "test -f retry.txt"))
    _configure_diagnosis(bench)
    snag = {"code": "logic", "path": "retry.txt", "line": 1, "message": message,
            "paved_road": "repair the fixture"}
    first_review: list[str] = []

    def diagnosis(_req):
        review = read_review((bench.repo / "tickets" / stem / "review.md").read_text())
        first_review.extend(finding.message for finding in review.findings)
        return json.dumps({"verdict": "retry", "lessons": ["Repair the first review finding."]})

    bench.script([lambda req: _commit(req, {"retry.txt": "first\n"}),
                  json.dumps({"verdict": "snag", "summary": "snag", "findings": [snag]}),
                  diagnosis,
                  lambda req: _commit(req, {"retry.txt": "second\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    report = await bench.drain()

    assert stem in report.merged
    assert [terminal["to"] for terminal in _terminals(bench, stem)] == ["gate_failed", "merged"]
    assert draws(bench.journal.read(), stem, "retry") == 1
    assert first_review == [message]
    return Observation("review_red_then_green_merges_with_one_retry", f"{stem}/1")


MEMBERS = (
    Member("bad_schema", "drain", "committed ticket misses a required section",
           "invalid_committed_ticket_reported_without_dispatch", _bad_schema),
    Member("premise_park_release", "drain", "premise_failed ticket is unchanged then corrected",
           "unchanged_premise_is_parked_then_content_change_releases", _premise_park_release),
    Member("red_then_green", "drain", "first Review rejects and second approves",
           "review_red_then_green_merges_with_one_retry", _red_then_green),
)
