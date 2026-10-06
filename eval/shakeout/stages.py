"""Fault-injection members for the production stage pipeline."""

import json
import os
import subprocess
from pathlib import Path

from chupa.artifacts import Finding
from chupa.box import BOX_DIR, Box
from chupa.config import Candidate, Route
from chupa.journal import EventType
from chupa.llm import LLMRequest
from chupa.seams import LocalFileSystem
from chupa.stages import Invoice, read_review
from eval.shakeout.bench import Bench
from eval.shakeout.run import Member, Observation


def _ticket(stem: str, fence: str, verification: str) -> str:
    return f"""---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- config.yaml

## Goal / Why
Exercise the stage fixture `{stem}`.

## Scope in / Scope out
In: this fixture. Out: every other fixture.

## Scope fence
- {fence}

## Acceptance criteria
1. `{verification.splitlines()[0]}` exits with the scripted stage outcome.

## Verification
```
{verification}
```

## Definition of rejected
The scripted observable is absent.

## Time budget
- expected: 10m
- stuck: 20m
"""


def _reply(outcome: str = "ok") -> str:
    return json.dumps({"outcome": outcome, "summary": "fixture", "surprises": "none",
                       "dead_ends": "none", "predicted_vs_actual": "10m predicted, 1m actual",
                       "findings": []})


def _diagnosis(verdict: str) -> str:
    return json.dumps({"verdict": verdict, "lessons": ["Follow the harvested finding."]})


def _commit(req: LLMRequest, files: dict[str, str]) -> str:
    assert req.worktree is not None
    for name, content in files.items():
        target = req.worktree / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    env = {**os.environ, "GIT_AUTHOR_NAME": "shakeout", "GIT_AUTHOR_EMAIL": "shakeout@example.invalid",
           "GIT_COMMITTER_NAME": "shakeout", "GIT_COMMITTER_EMAIL": "shakeout@example.invalid"}
    subprocess.run(["git", "-C", str(req.worktree), "add", *files], env=env, check=True)
    subprocess.run(["git", "-C", str(req.worktree), "commit", "-m", "shakeout fixture"],
                   env=env, check=True, capture_output=True)
    return _reply()


def _terminal(bench: Bench, stem: str) -> dict:
    return next(event.body for event in reversed(bench.journal.read())
                if event.type == EventType.STATE_TRANSITION and event.ticket == stem
                and event.body.get("to") != "running")


def _configure_diagnosis(bench: Bench) -> None:
    route = Route(tier="medium", surface="diagnose", candidates=[Candidate(provider="fake")])
    bench.configure(bench.config.model_copy(update={
        "routing": [*bench.config.routing, route],
        "caps": bench.config.caps.model_copy(update={"retry": 1}),
    }))


def _finding(bench: Bench, stem: str, code: str) -> Finding:
    path = bench.repo / "tickets" / stem / "attempts" / "0" / "harvest.json"
    payload = json.loads(path.read_text())
    return next(Finding.model_validate(item) for item in payload["findings"] if item["code"] == code)


async def _scope_escape(bench: Bench) -> Observation:
    stem = "scope-escape"
    bench.add_ticket(stem, _ticket(stem, "inside.txt", "true"))
    _configure_diagnosis(bench)
    action = lambda req: _commit(req, {"inside.txt": "ok\n", "outside.txt": "escape\n"})
    bench.script([action, _diagnosis("reject"), action])
    report = await bench.drain()
    terminal = _terminal(bench, stem)
    invoice = Invoice.model_validate_json((bench.repo / "tickets" / stem / "checks.json").read_text())
    scope = next(item for item in invoice.reports if item.code == "scope_fence")
    finding = _finding(bench, stem, "scope_fence")
    assert terminal == {"to": "gate_failed", "stage": "check", "reason": "scope_fence",
                        "dispatch": "reject_queue", "routed": "reject_queue"}
    assert [item.path for item in scope.findings] == ["outside.txt"]
    assert finding.path == "outside.txt" and stem not in report.merged
    return Observation("scope_fence_harvested", f"{stem}/0")


async def _unfixable_lint_branch_only(bench: Bench) -> Observation:
    stem = "unfixable-lint"
    bench.add_ticket(stem, _ticket(stem, "branch-only.py", "test ! -f branch-only.py"))
    _configure_diagnosis(bench)
    action = lambda req: _commit(req, {"branch-only.py": "broken\n"})
    bench.script([action, _diagnosis("reject"), action])
    report = await bench.drain()
    terminal = _terminal(bench, stem)
    invoice = Invoice.model_validate_json((bench.repo / "tickets" / stem / "checks.json").read_text())
    finding = _finding(bench, stem, "verification")
    assert terminal["to"] == "gate_failed" and terminal["stage"] == "check"
    assert terminal["routed"] == "reject_queue" and not any(item.base_red for item in invoice.verification)
    assert finding.code == "verification" and stem not in report.merged
    return Observation("branch_only_verification_rejected", f"{stem}/0")


async def _review_reject(bench: Bench) -> Observation:
    stem = "review-reject"
    bench.add_ticket(stem, _ticket(stem, "review.txt", "test -f review.txt"))
    _configure_diagnosis(bench)
    snag = {"code": "logic", "path": "review.txt", "line": 1, "message": "snagged fixture",
            "paved_road": "repair the fixture"}
    action = lambda req: _commit(req, {"review.txt": "ok\n"})
    verdict = json.dumps({"verdict": "snag", "summary": "snag", "findings": [snag]})
    bench.script([action, verdict, _diagnosis("reject"), action, verdict])
    report = await bench.drain()
    terminal = _terminal(bench, stem)
    review = read_review((bench.repo / "tickets" / stem / "review.md").read_text())
    assert terminal["to"] == "gate_failed" and terminal["stage"] == "review"
    assert review.verdict == "snag" and review.findings[0].message == "snagged fixture"
    assert stem not in report.merged
    return Observation("review_snag_pinned", f"{stem}/0")


async def _review_reject_reentry(bench: Bench) -> Observation:
    stem = "review-reentry"
    bench.add_ticket(stem, _ticket(stem, "reentry.txt", "test -f reentry.txt"))
    _configure_diagnosis(bench)
    message = "unique reentry finding"
    snag = {"code": "logic", "path": "reentry.txt", "line": 1, "message": message,
            "paved_road": "repair the fixture"}
    bench.script([lambda req: _commit(req, {"reentry.txt": "first\n"}),
                  json.dumps({"verdict": "snag", "summary": "snag", "findings": [snag]}),
                  _diagnosis("retry"), lambda req: _commit(req, {"reentry.txt": "second\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    report = await bench.drain()
    prompts = [request.rendered for request in bench.llm.requests if request.surface == "implement"]
    second = prompts[1]
    criteria = second.split("## Acceptance criteria", 1)[1].split("## Verification", 1)[0]
    assert message in criteria and stem in report.merged
    return Observation("review_finding_in_reentry_criteria", f"{stem}/1")


async def _empty_committed_diff(bench: Bench) -> Observation:
    stem = "empty-committed-diff"
    bench.add_ticket(stem, _ticket(stem, "empty.txt", "true"))
    _configure_diagnosis(bench)
    bench.script([_reply(), _diagnosis("reject"), _reply()])
    report = await bench.drain()
    terminal = _terminal(bench, stem)
    finding = _finding(bench, stem, "verification")
    assert terminal["to"] == "gate_failed" and terminal["stage"] == "check"
    assert finding.message == "the branch carries no committed change" and stem not in report.merged
    return Observation("empty_diff_harvested", f"{stem}/0")


async def _base_diff_attribution(bench: Bench) -> Observation:
    stem = "base-diff-attribution"
    bench.add_ticket(stem, _ticket(stem, "green.txt", "test -f red-on-base.txt\ntest -f green.txt"))
    bench.script([lambda req: _commit(req, {"green.txt": "green\n"}),
                  json.dumps({"verdict": "approve", "summary": "approved", "findings": []})])
    report = await bench.drain()
    invoice = Invoice.model_validate_json((bench.repo / "tickets" / stem / "checks.json").read_text())
    messages = Box(bench.config.state_dir / BOX_DIR, LocalFileSystem()).messages()
    assert stem in report.merged and not any(event.type == EventType.CAP_CONSUMED and event.ticket == stem
                                             and event.body.get("cap") == "retry"
                                             for event in bench.journal.read())
    assert [item.base_red for item in invoice.verification] == [True, False]
    assert len(messages) == 1 and messages[0].outcome == "base_red"
    return Observation("base_red_attributed", f"{stem}/0")


MEMBERS = (
    Member("scope_escape", "stages", "commit outside the scope fence", "scope_fence_harvested", _scope_escape),
    Member("unfixable_lint_branch_only", "stages", "branch-only verification failure", "branch_only_verification_rejected",
           _unfixable_lint_branch_only),
    Member("review_reject", "stages", "review replies snag", "review_snag_pinned", _review_reject),
    Member("review_reject_reentry", "stages", "review rejects then approves", "review_finding_in_reentry_criteria",
           _review_reject_reentry),
    Member("empty_committed_diff", "stages", "Implement commits nothing", "empty_diff_harvested",
           _empty_committed_diff),
    Member("base_diff_attribution", "stages", "base and branch are both red", "base_red_attributed",
           _base_diff_attribution),
)
