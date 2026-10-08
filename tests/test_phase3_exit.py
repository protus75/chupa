"""Phase 3 exit reads the producer's committed evidence, never live daemon state."""

from pathlib import Path
import re

import yaml
import pytest

from chupa.artifacts import DAEMON_SOAK_MEMBERS, DAEMON_SOAK_REPORT, DaemonSoakReport
from chupa.tickets import _bullets, _sections, ticket_path

ROOT = Path(__file__).resolve().parent.parent


def _dependencies(stem):
    path = ticket_path(stem)
    assert (ROOT / path).is_file(), f"premise_failed: missing predecessor {path}"
    sections, errors = _sections((ROOT / path).read_text(), path)
    assert not errors, f"premise_failed: {path}: {errors}"
    body = sections["Depends on"]
    if body.strip() == "none":
        return ()
    edges, errors = _bullets(body, "Depends on", path)
    assert not errors, f"premise_failed: {path}: {errors}"
    return tuple(edges)


def test_phase3_exit_dependency_coverage():
    plan = (ROOT / "CHUPA_PLAN.md").read_text()
    registry = yaml.safe_load(re.search(
        r"^# BEGIN_REGISTRY_P3\n(.*?)^# END_REGISTRY_P3$", plan, re.M | re.S)[1])
    assert registry["admissions"][-1] == ["phase3-exit"]
    preceding = {stem for admission in registry["admissions"][:-1] for stem in admission}
    assert _dependencies("phase3-exit") == ("phase3-continue-27",)
    reached = set()
    pending = list(_dependencies("phase3-exit"))
    while pending:
        stem = pending.pop()
        if stem not in reached:
            reached.add(stem)
            pending.extend(_dependencies(stem))
    assert preceding <= reached, f"premise_failed: uncovered Phase 3 members {preceding - reached}"
    assert {"daemon-soak", "daemon-soak-runner", "soak-run"} <= preceding & reached


def test_phase3_exit_reads_committed_soak_report():
    # Check and merged-main runs consume this tracked producer output in their clean checkout.
    # The machinery's unchanged suites prove production derivation and checks-only custody.
    path = ROOT / "tickets" / "soak-run" / DAEMON_SOAK_REPORT
    assert path.is_file(), f"premise_failed: missing committed artifact {path.relative_to(ROOT)}"
    try:
        report = DaemonSoakReport.model_validate_json(path.read_bytes())
    except ValueError as error:
        pytest.fail(f"premise_failed: {path.relative_to(ROOT)} schema: {error}")
    assert tuple(entry.member for entry in report.entries) == DAEMON_SOAK_MEMBERS
    assert re.fullmatch(r"[0-9a-f]{40}", report.produced_at_sha), "premise_failed: soak source provenance"
    assert report.produced_by_spec_version > 0
    for entry in report.entries:
        assert entry.green, f"premise_failed: {entry.member} is red"
        assert entry.observed == entry.expected, f"premise_failed: {entry.member} observation"
        assert not entry.auditor, f"premise_failed: {entry.member} auditor: {entry.auditor}"
        assert entry.producing_run and entry.planted_fault, f"premise_failed: {entry.member} provenance"
