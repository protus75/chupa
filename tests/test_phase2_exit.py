"""Phase 2 exit reads from the battery's committed emitter artifacts (19.P2)."""

from pathlib import Path

from chupa.artifacts import SHAKEOUT_REPORT, ShakeoutReport
from chupa.stages import Invoice

ROOT = Path(__file__).resolve().parent.parent
PRODUCER = ROOT / "tickets" / "shakeout-providers"

MEMBERS = {
    "scope_escape", "unfixable_lint_branch_only", "review_reject", "review_reject_reentry",
    "empty_committed_diff", "base_diff_attribution", "invalid_output_exhausted",
    "stuck_budget_kill", "premise_false", "timeout_dead_ends", "identical_terminals",
    "bad_schema", "premise_park_release", "red_then_green", "engine_death_mid_call",
    "conflicted_rebase", "auth_expiry", "planted_secret",
}


def test_committed_battery_report_has_every_green_member_and_auditor():
    report = ShakeoutReport.model_validate_json((PRODUCER / SHAKEOUT_REPORT).read_text())
    assert {entry.member for entry in report.entries} == MEMBERS
    assert all(entry.green and not entry.auditor for entry in report.entries)


def test_producer_check_ran_the_required_battery_verification():
    invoice = Invoice.model_validate_json((PRODUCER / "checks.json").read_text())
    assert invoice.stem == "shakeout-providers"
    assert invoice.passed
    assert any(report.code == "verification" and report.verdict == "pass"
               for report in invoice.reports)
