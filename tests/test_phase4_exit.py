"""Phase 4 consumes committed producer evidence; production proofs run unchanged at Check."""

import asyncio
import os
from pathlib import Path
import re

import pytest
import yaml

from chupa.artifacts import (
    RELIABILITY_BATTERY_MEMBERS, RELIABILITY_BATTERY_REPORT,
    RELIABILITY_BATTERY_SPEC_VERSION, ReliabilityBatteryReport,
)
from chupa.git import Git, GitError
from chupa.seams import SubprocessExec
from chupa.stages import Invoice
from chupa.tickets import _bullets, _sections, split_frontmatter, ticket_path

ROOT = Path(__file__).resolve().parents[1]
PHASE4_DELIVERABLES = (
    "watchdog-event-stream", "notify-transport", "watchdog-detector",
    "watchdog-activation", "provider-cooldown-failover", "reliability-battery",
    "reliability-run",
)


def _git(*argv):
    return asyncio.run(Git(SubprocessExec(), env=os.environ, timeout=30)._run(ROOT, *argv))


def _committed(path):
    try:
        return _git("show", f"HEAD:{path}")
    except GitError as error:
        pytest.fail(f"premise_failed: committed exit read {path}: {error}")


def _dependencies(stem):
    path = ticket_path(stem)
    text = _committed(path)
    frontmatter, _ = split_frontmatter(text)
    assert yaml.safe_load(frontmatter)["state"] != "rejected", (
        f"premise_failed: predecessor {path} is rejected; require its merged same-goal successor and rewired coverage")
    sections, errors = _sections(text, path)
    assert not errors, f"premise_failed: predecessor {path}: {errors}"
    body = sections["Depends on"]
    if body.strip() in {"none", "- none"}:
        return ()
    edges, errors = _bullets(body, "Depends on", path)
    assert not errors, f"premise_failed: predecessor {path}: {errors}"
    return tuple(edges)


def test_phase4_exit_dependency_coverage():
    registry = yaml.safe_load(re.search(
        r"^# BEGIN_REGISTRY_P4\n(.*?)^# END_REGISTRY_P4$",
        _committed("CHUPA_PLAN.md"), re.M | re.S)[1])
    assert registry["admissions"][-1] == ["phase4-exit"]
    preceding = tuple(stem for admission in registry["admissions"][:-1] for stem in admission)
    assert preceding == PHASE4_DELIVERABLES
    assert _dependencies("phase4-exit") == ("phase4-continue-05",)
    reached, pending = set(), list(_dependencies("phase4-exit"))
    while pending:
        stem = pending.pop()
        if stem not in reached:
            reached.add(stem)
            pending.extend(_dependencies(stem))
    assert reached & set(registry["seeds"]) == set(PHASE4_DELIVERABLES), (
        f"premise_failed: Phase 4 dependency coverage missing {set(preceding) - reached}")
    # Dispatch supplies settlement proof. Code presence reads only the existing Git seam's trailers;
    # the no-code report producer has a null code commit and therefore no squash trailer.
    trailers = set(_git("log", "--format=%(trailers:key=chupa-ticket,valueonly)").split())
    assert set(preceding) - {"reliability-run"} <= trailers, (
        f"premise_failed: code-deliverable chupa-ticket trailers {set(preceding) - {'reliability-run'} - trailers}")


def test_phase4_exit_reads_committed_reliability_report():
    path = f"tickets/reliability-run/{RELIABILITY_BATTERY_REPORT}"
    try:
        report = ReliabilityBatteryReport.model_validate_json(_committed(path))
    except ValueError as error:
        pytest.fail(f"premise_failed: {path} schema: {error}")
    assert tuple(e.member for e in report.entries) == RELIABILITY_BATTERY_MEMBERS == (
        "classified_quota_exhaustion", "all_candidates_cooling_recovery",
        "unclassified_failure_preservation",
    ), f"premise_failed: {path} closed member order"
    assert re.fullmatch(r"[0-9a-f]{40}", report.produced_at_sha), f"premise_failed: {path} source provenance"
    assert report.produced_by_spec_version == RELIABILITY_BATTERY_SPEC_VERSION, (
        f"premise_failed: {path} spec provenance")
    for entry in report.entries:
        assert entry.green, f"premise_failed: {path} member {entry.member} red"
        assert entry.observed == entry.expected, f"premise_failed: {path} member {entry.member} observation"
        assert entry.auditor == [], f"premise_failed: {path} member {entry.member} auditor"
        assert entry.producing_run and entry.planted_fault, f"premise_failed: {path} member {entry.member} provenance"


def _watchdog_receipt():
    path = "tickets/watchdog-activation/checks.json"
    try:
        invoice = Invoice.model_validate_json(_committed(path))
    except ValueError as error:
        pytest.fail(f"premise_failed: {path} schema: {error}")
    assert invoice.stem == "watchdog-activation" and invoice.passed, f"premise_failed: {path} passed"
    assert "verification" not in invoice.bypassed, f"premise_failed: {path} verification bypass"
    reports = [r for r in invoice.reports if r.code == "verification"]
    assert len(reports) == 1 and reports[0].verdict == "pass" and not reports[0].findings, (
        f"premise_failed: {path} verification report")
    commands = [v for v in invoice.verification
                if v.argv[:3] == ["uv", "run", "pytest"] and "tests/test_watchdog_activation.py" in v.argv]
    assert commands and all(v.rc == 0 for v in commands), f"premise_failed: {path} watchdog Verification command"
    return invoice


def test_phase4_exit_reads_committed_soft_band_check():
    # This is a suite-level receipt, never per-test results. The named merged proof is run at Check.
    _watchdog_receipt()


def test_phase4_exit_reads_committed_hard_timeout_check():
    _watchdog_receipt()
