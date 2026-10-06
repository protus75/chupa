"""Shakeout report custody and cumulative double gate."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from chupa.artifacts import ShakeoutEntry, ShakeoutReport
from chupa.journal import EventType
from eval.shakeout.bench import Bench
from eval.shakeout import run as shakeout
from eval.shakeout.driver import MEMBERS as DRIVER_MEMBERS
from eval.shakeout.runner import MEMBERS as RUNNER_MEMBERS
from eval.shakeout.stages import MEMBERS


def entry(member: str, observed: str = "ok") -> ShakeoutEntry:
    return ShakeoutEntry(member=member, group="first", planted_fault="fault", expected="ok",
                         observed=observed, producing_run=f"{member}/0", auditor=[], green=observed == "ok")


def report(*entries: ShakeoutEntry) -> ShakeoutReport:
    return ShakeoutReport(produced_by_spec_version=1, produced_at_sha="abc", entries=list(entries))


def test_produce_requires_complete_matching_prior_and_returns_cumulative(tmp_path, monkeypatch):
    observed = {"first": "ok"}

    async def first_run(bench):
        return shakeout.Observation(observed["first"], "first_member/0")

    async def second_run(bench):
        return shakeout.Observation("ok", "second_member/0")

    first = shakeout.Member("first_member", "first", "fault", "ok", first_run)
    second = shakeout.Member("second_member", "second", "fault", "ok", second_run)
    modules = {"eval.shakeout.first": SimpleNamespace(MEMBERS=(first,)),
               "eval.shakeout.second": SimpleNamespace(MEMBERS=(second,))}
    monkeypatch.setattr(shakeout, "GROUPS", ("first", "second"))
    monkeypatch.setattr(shakeout.importlib, "import_module", modules.__getitem__)

    with pytest.raises(shakeout.ShakeoutRefused, match="first_member"):
        asyncio.run(shakeout.produce("second", report(), tmp_path / "missing"))
    observed["first"] = "different"
    with pytest.raises(shakeout.ShakeoutRefused, match="first_member"):
        asyncio.run(shakeout.produce("second", report(entry("first_member")), tmp_path / "different"))
    observed["first"] = "ok"
    produced = asyncio.run(shakeout.produce("second", report(entry("first_member")), tmp_path / "green"))
    assert [item.member for item in produced.entries] == ["first_member", "second_member"]
    assert all(item.green for item in produced.entries)


def test_member_auditor_blocks_double_terminal_and_schema_blocks_false_green(tmp_path):
    async def planted(bench):
        bench.journal.append(EventType.STATE_TRANSITION, {"to": "running"}, ticket="fault")
        bench.journal.append(EventType.STATE_TRANSITION, {"to": "gate_failed"}, ticket="fault")
        bench.journal.append(EventType.STATE_TRANSITION, {"to": "timeout"}, ticket="fault")
        return shakeout.Observation("ok", "double_terminal/0")

    member = shakeout.Member("double_terminal", "first", "double terminal", "ok", planted)
    result = asyncio.run(shakeout.run_member(member, tmp_path))
    assert result.green is False
    assert any("one_terminal_per_run" in line for line in result.auditor)
    with pytest.raises(ValidationError):
        ShakeoutEntry.model_validate(result.model_dump() | {"green": True})


def test_bench_configure_preserves_seams_and_changes_cap(tmp_path):
    bench = Bench(tmp_path / "bench")
    asyncio.run(bench.initialize())
    journal, clock, repo, llm = bench.journal, bench.clock, bench.repo, bench.llm
    replacement = bench.config.model_copy(update={"caps": bench.config.caps.model_copy(update={"retry": 2})})
    bench.configure(replacement)
    assert bench.config.caps.retry == 2
    assert (bench.journal, bench.clock, bench.repo, bench.llm) == (journal, clock, repo, llm)
    assert bench._checkout.config.caps.retry == 2
    assert bench._pipeline() is not None


def test_bench_drain_uses_production_pipeline(tmp_path):
    bench = Bench(tmp_path / "bench")
    ticket = """---
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
Add the fixture.

## Scope in / Scope out
In: fixture. Out: rest.

## Scope fence
- src/thing.txt

## Acceptance criteria
1. `grep -q ok src/thing.txt` exits 0.

## Verification
```
grep -q ok src/thing.txt
```

## Definition of rejected
The fixture is absent.

## Time budget
- expected: 10m
- stuck: 20m
"""
    bench.add_ticket("fixture", ticket)

    def implement(req):
        target = req.worktree / "src" / "thing.txt"
        target.parent.mkdir(parents=True)
        target.write_text("ok\n")
        subprocess.run(["git", "-C", str(req.worktree), "add", "src/thing.txt"], env=bench.env, check=True)
        subprocess.run(["git", "-C", str(req.worktree), "commit", "-m", "fixture"],
                       env=bench.env, check=True, capture_output=True)
        return json.dumps({"outcome": "ok", "summary": "wrote fixture", "surprises": "none",
                           "dead_ends": "none", "predicted_vs_actual": "10m predicted, 1m actual", "findings": []})

    bench.script([implement, json.dumps({"verdict": "approve", "summary": "checked", "findings": []})])
    result = asyncio.run(bench.drain())
    assert result.merged == ["fixture"], result.render()
    assert bench.report is result
    assert (bench.repo / "src" / "thing.txt").read_text() == "ok\n"


def test_unknown_group_command_exits_two(tmp_path):
    result = subprocess.run([sys.executable, "-m", "eval.shakeout.run", "--group", "nope",
                             "--out", str(tmp_path / "x.json")], check=False)
    assert result.returncode == 2
    assert not (tmp_path / "x.json").exists()


def test_scope_escape_member_observes_check_failure_and_no_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(MEMBERS[0], tmp_path))
    assert result.green and result.observed == "scope_fence_harvested"


def test_unfixable_lint_branch_only_member_observes_check_failure_and_no_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(MEMBERS[1], tmp_path))
    assert result.green and result.observed == "branch_only_verification_rejected"


def test_review_reject_member_observes_snag_and_no_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(MEMBERS[2], tmp_path))
    assert result.green and result.observed == "review_snag_pinned"


def test_review_reject_reentry_member_observes_criteria_position_reentry_and_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(MEMBERS[3], tmp_path))
    assert result.green and result.observed == "review_finding_in_reentry_criteria"


def test_empty_committed_diff_member_observes_check_failure_and_no_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(MEMBERS[4], tmp_path))
    assert result.green and result.observed == "empty_diff_harvested"


def test_base_diff_attribution_member_observes_base_red_and_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(MEMBERS[5], tmp_path))
    assert result.green and result.observed == "base_red_attributed"


def test_produce_stages_returns_six_green_entries(tmp_path):
    produced = asyncio.run(shakeout.produce("stages", None, tmp_path))
    assert [entry.member for entry in produced.entries] == [member.id for member in MEMBERS]
    assert len(produced.entries) == 6 and all(entry.green for entry in produced.entries)


def test_invalid_output_exhausted_member_observes_bounded_reprompts_and_harvest(tmp_path):
    result = asyncio.run(shakeout.run_member(DRIVER_MEMBERS[0], tmp_path))
    assert result.green and result.observed == "invalid_artifact_harvested_after_bounded_reprompts"


def test_stuck_budget_kill_member_observes_abort_harvest_and_followup_merge(tmp_path):
    result = asyncio.run(shakeout.run_member(DRIVER_MEMBERS[1], tmp_path))
    assert result.green and result.observed == "timeout_harvest_reason_after_stuck_kill"


def test_premise_false_member_observes_harvest_and_premise_park(tmp_path):
    result = asyncio.run(shakeout.run_member(RUNNER_MEMBERS[0], tmp_path))
    assert result.green and result.observed == "premise_harvested_without_reoffer"


def test_timeout_dead_ends_member_observes_lesson_on_second_attempt(tmp_path):
    result = asyncio.run(shakeout.run_member(RUNNER_MEMBERS[1], tmp_path))
    assert result.green and result.observed == "timeout_lesson_rendered_on_retry"


def test_identical_terminals_member_observes_escalation_at_k(tmp_path):
    result = asyncio.run(shakeout.run_member(RUNNER_MEMBERS[2], tmp_path))
    assert result.green and result.observed == "identical_reason_escalates_at_k"
