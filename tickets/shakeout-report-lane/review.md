# Review: snag

The registration, lift gating and runner largely match the ticket, but acceptance criterion 2's report-required test is missing, and the check that a Verification command names the report only matches a whole argv element.

## Findings

- [acceptance] tests/test_stages.py:338 Criterion 2 requires a test showing that a Check fails `verification` when a Verification command names `tickets/<stem>/shakeout-report.json` but leaves no report, even when every command is otherwise excused. No added test covers this. `test_stale_registered_report_is_deleted_before_verification` keeps the default Verification, which does not name the report, so the REPORT REQUIRED path in `check` never runs in any test. (do instead: Add a test whose TICKET Verification names `tickets/<stem>/shakeout-report.json`, for example `--out tickets/<stem>/shakeout-report.json` on a command that exits 0 without writing the file. Assert the Check is `gate_failed` with one finding coded `verification` on that path.)
- [logic] chupa/stages.py:788 `ticket.verification` is `tuple[tuple[str, ...], ...]`, so `f"{TICKETS_DIR}/{stem}/{name}" in argv` tests whether one whole argv element equals the path. A command that names the report inside a larger element, such as `--out=tickets/<stem>/shakeout-report.json` or `sh -c '... > tickets/<stem>/shakeout-report.json'`, does not count as naming it. The Check then passes with no report in the outbox, which the Definition of rejected forbids. (do instead: Treat the report as named when any argv element contains the path as a substring, for example `any(target in arg for arg in argv)`. Add a test case that uses an `--out=` style argument.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "117efe2ea203f10e1b1f6a6ed3bea3d172e80ee7",
  "stem": "shakeout-report-lane",
  "reviewed_sha": "117efe2ea203f10e1b1f6a6ed3bea3d172e80ee7",
  "summary": "The registration, lift gating and runner largely match the ticket, but acceptance criterion 2's report-required test is missing, and the check that a Verification command names the report only matches a whole argv element.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": 338,
      "message": "Criterion 2 requires a test showing that a Check fails `verification` when a Verification command names `tickets/<stem>/shakeout-report.json` but leaves no report, even when every command is otherwise excused. No added test covers this. `test_stale_registered_report_is_deleted_before_verification` keeps the default Verification, which does not name the report, so the REPORT REQUIRED path in `check` never runs in any test.",
      "paved_road": "Add a test whose TICKET Verification names `tickets/<stem>/shakeout-report.json`, for example `--out tickets/<stem>/shakeout-report.json` on a command that exits 0 without writing the file. Assert the Check is `gate_failed` with one finding coded `verification` on that path."
    },
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 788,
      "message": "`ticket.verification` is `tuple[tuple[str, ...], ...]`, so `f\"{TICKETS_DIR}/{stem}/{name}\" in argv` tests whether one whole argv element equals the path. A command that names the report inside a larger element, such as `--out=tickets/<stem>/shakeout-report.json` or `sh -c '... > tickets/<stem>/shakeout-report.json'`, does not count as naming it. The Check then passes with no report in the outbox, which the Definition of rejected forbids.",
      "paved_road": "Treat the report as named when any argv element contains the path as a substring, for example `any(target in arg for arg in argv)`. Add a test case that uses an `--out=` style argument."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
