"""Terminal reads of harness-produced evidence, without fixture or live-state access."""

import asyncio
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from chupa.artifacts import (HOST_LOOP_REPORT, EXIT_RECEIPT, REVIEW_BASELINE_REPORT,
                            HostLoopReport, ExitReceipt, ReviewBaselineReport)
from chupa.git import Git, GitError
from chupa.seams import SubprocessExec
from chupa.tickets import _bullets, _sections, split_frontmatter, Frontmatter, ticket_path
from eval import host_loop

ROOT = Path(__file__).resolve().parents[1]
# Freeze dependency history at dispatch; the exit's reports are read from their paths.
EXIT_HEAD = "70167b1574baa14899ec14c8e320c49ab14cdf25"
PHASE_START = "e0726bb8b9f0e3e7d19b17ffacfa7662821e750e"
PAYLOADS = ("core-renderer", "core-drift-classifier", "core-drift-activation",
            "migrate-config", "host-contract-doc", "fixture-host-scaffold", "bug-gate-grammar",
            "report-inbox-triage", "escape-column", "supervised-merge-hold",
            "go-grade-machinery", "go-grade-run", "exit-receipt-machinery")
LOOP_PATH = ROOT / "tickets/phase6-exit" / HOST_LOOP_REPORT
RECEIPT_PATH = ROOT / "tickets/phase6-exit" / EXIT_RECEIPT
BASELINE_PATH = ROOT / "tickets/go-grade-run" / REVIEW_BASELINE_REPORT


def _git():
    return Git(SubprocessExec(), env={"PATH": "/usr/bin:/bin"}, timeout=30)


@lru_cache
def _dependencies(stem):
    path = ticket_path(stem)
    text = asyncio.run(_git()._run(ROOT, "show", f"{EXIT_HEAD}:{path}"))
    raw, body = split_frontmatter(text)
    import yaml
    frontmatter = Frontmatter.model_validate(yaml.safe_load(raw))
    assert frontmatter.state != "rejected", f"premise_failed: {stem} needs a merged successor"
    sections, errors = _sections(body, path)
    assert not errors
    if sections["Depends on"] in {"none", "- none"}:
        return ()
    edges, errors = _bullets(sections["Depends on"], "Depends on", path)
    assert not errors
    return tuple(edges)


@pytest.fixture(scope="module")
def baseline_bytes():
    # Existing reader proves the baseline bytes are committed, without reading a journal.
    return asyncio.run(host_loop.committed_bytes(_git(), ROOT, BASELINE_PATH))


def _reports():
    # Missing OUTBOX evidence fails here, including before Check has lifted it to main.
    return (HostLoopReport.model_validate_json(LOOP_PATH.read_bytes()),
            ExitReceipt.model_validate_json(RECEIPT_PATH.read_bytes()))


def _green(entry, member, producing_run, observation):
    assert entry.member == member
    assert entry.producing_run == producing_run
    assert entry.expected == entry.observed == observation
    assert entry.engine_plane_edits == entry.auditor == []
    assert entry.green is True


def _validate_receipt(loop_bytes, baseline_bytes, receipt_bytes):
    receipt = ExitReceipt.model_validate_json(receipt_bytes)
    regenerated = host_loop.regenerate(loop_bytes, baseline_bytes)
    assert receipt.reads.model_dump() == regenerated.reads.model_dump() == {
        "machine_ticket_merge": "pass", "report_to_regression_bug_loop": "pass",
        "escape_attribution": "pass", "go_grade_report": "pass"}
    assert receipt.host_loop_digest == hashlib.sha256(loop_bytes).hexdigest()
    assert receipt.baseline_report_digest == hashlib.sha256(baseline_bytes).hexdigest()
    baseline = ReviewBaselineReport.model_validate_json(baseline_bytes)
    assert receipt.verdict_signal == regenerated.verdict_signal == baseline.verdict_signal
    assert host_loop.canonical(regenerated) == receipt_bytes
    return receipt


def test_phase6_exit_transitive_dependencies(baseline_bytes):
    assert _dependencies("phase6-exit") == ("phase6-continue-08", "exit-receipt-machinery")
    reached, pending = set(), list(_dependencies("phase6-exit"))
    while pending:
        stem = pending.pop()
        if stem not in reached:
            reached.add(stem)
            pending.extend(_dependencies(stem))
    assert set(PAYLOADS) <= reached, f"premise_failed: missing Phase 6 coverage {set(PAYLOADS) - reached}"
    squashes = asyncio.run(_git().first_parent_squashes(ROOT, f"{PHASE_START}..{EXIT_HEAD}"))
    merged = {row["ticket"] for row in squashes}
    assert set(PAYLOADS) - {"go-grade-run"} <= merged
    # The no-code producer has no code squash; its committed report is its evidence.
    assert "go-grade-machinery" in _dependencies("go-grade-run")
    assert "go-grade-run" in _dependencies("exit-receipt-machinery")
    ReviewBaselineReport.model_validate_json(baseline_bytes)


def test_phase6_exit_machine_ticket_merge():
    report, receipt = _reports()
    merges = report.entries[:-2]
    assert len(merges) >= 3
    assert len({entry.producing_run for entry in merges}) == len(merges)
    assert [entry.producing_run for entry in merges[:3]] == [
        "merge-add/0", "merge-bonus/0", "merge-floor/0"]
    for entry in merges:
        _green(entry, "machine_ticket_merge", entry.producing_run, "machine_ticket_merged")
    assert receipt.reads.machine_ticket_merge == "pass"


def test_phase6_exit_report_to_regression_bug_loop():
    report, receipt = _reports()
    _green(report.entries[-2], "report_to_regression_bug_loop", "regression/0",
           "report_replayed_regression_bug_merged")
    assert receipt.reads.report_to_regression_bug_loop == "pass"


def test_phase6_exit_escape_attribution():
    report, receipt = _reports()
    _green(report.entries[-1], "escape_attribution", "escape/0",
           "escape_attributed_by_squash_trailers")
    assert receipt.reads.escape_attribution == "pass"


def test_phase6_exit_go_grade_report(baseline_bytes):
    baseline = ReviewBaselineReport.model_validate_json(baseline_bytes)
    _, receipt = _reports()
    assert receipt.reads.go_grade_report == "pass"
    actual_signal = json.loads(baseline_bytes)["verdict_signal"]
    assert receipt.verdict_signal.model_dump(mode="json") == actual_signal
    assert baseline.verdict_signal.body.verdict in {"GO", "NO_GO"}
    if not baseline.complete:
        assert baseline.verdict_signal.body.verdict == "NO_GO"
        partial_go = json.loads(baseline_bytes)
        partial_go["verdict_signal"]["body"]["verdict"] = "GO"
        with pytest.raises(ValidationError, match="GO requires complete"):
            host_loop.regenerate(LOOP_PATH.read_bytes(), json.dumps(partial_go).encode())
    invalid = json.loads(baseline_bytes)
    invalid["verdict_signal"]["body"]["identity"]["review"]["rows"].pop("low")
    with pytest.raises(ValidationError):
        host_loop.regenerate(LOOP_PATH.read_bytes(), json.dumps(invalid).encode())


def test_phase6_exit_receipt_regeneration(baseline_bytes, tmp_path, monkeypatch):
    loop_bytes, receipt_bytes = LOOP_PATH.read_bytes(), RECEIPT_PATH.read_bytes()
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path / ".chupa").exists()

    def forbidden(*args, **kwargs):
        pytest.fail("receipt regeneration accessed git or live state")

    monkeypatch.setattr(Git, "_run", forbidden)
    monkeypatch.setattr(host_loop.Journal, "read", forbidden)
    _validate_receipt(loop_bytes, baseline_bytes, receipt_bytes)
    assert host_loop.canonical(host_loop.regenerate(loop_bytes, baseline_bytes)) == receipt_bytes


@pytest.mark.parametrize("member", ["machine_ticket_merge", "report_to_regression_bug_loop",
                                   "escape_attribution"])
def test_phase6_exit_red_evidence_refuses(member, baseline_bytes):
    red = json.loads(LOOP_PATH.read_bytes())
    entry = next(entry for entry in red["entries"] if entry["member"] == member)
    entry.update(observed="unmet production evidence", green=False)
    with pytest.raises(AssertionError):
        _validate_receipt(json.dumps(red).encode(), baseline_bytes, RECEIPT_PATH.read_bytes())


@pytest.mark.parametrize("path_name", ["LOOP_PATH", "RECEIPT_PATH"])
def test_phase6_exit_missing_evidence_refuses(path_name, tmp_path, monkeypatch):
    missing = tmp_path / globals()[path_name].name
    assert not missing.exists()
    monkeypatch.setitem(globals(), path_name, missing)
    with pytest.raises(FileNotFoundError) as refused:
        _reports()
    assert refused.value.filename == str(missing)


def test_phase6_exit_missing_baseline_refuses(tmp_path):
    missing = ROOT / "tickets/phase6-exit" / f"{tmp_path.name}-{REVIEW_BASELINE_REPORT}"
    assert not missing.exists()
    with pytest.raises(GitError) as refused:
        asyncio.run(host_loop.committed_bytes(_git(), ROOT, missing))
    assert f"HEAD:{missing.relative_to(ROOT).as_posix()}" in refused.value.argv


@pytest.mark.parametrize("field", ["host_loop_digest", "baseline_report_digest"])
def test_phase6_exit_wrong_input_digest_refuses(field, baseline_bytes):
    receipt = json.loads(RECEIPT_PATH.read_bytes())
    receipt[field] = "0" * 64
    with pytest.raises(AssertionError):
        _validate_receipt(LOOP_PATH.read_bytes(), baseline_bytes, json.dumps(receipt).encode())


def test_phase6_exit_invalid_loop_refuses(baseline_bytes):
    invalid = json.loads(LOOP_PATH.read_bytes())
    invalid["entries"][0]["unknown"] = True
    with pytest.raises(ValidationError):
        _validate_receipt(json.dumps(invalid).encode(), baseline_bytes, RECEIPT_PATH.read_bytes())
