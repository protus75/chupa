# Review: snag

The engine changes look plausible, but tests/test_stages.py adds only the report-required test; the tests acceptance criteria 1 and 2 require for lifting and stale-report deletion are missing.

## Findings

- [acceptance] tests/test_stages.py:306 Acceptance criterion 1 is unmet. No test shows that a Check whose Verification writes a valid shakeout-report.json lifts it in the `chupa(<stem>): checks` commit. No test shows that a schema-invalid report makes the Check gate_failed and commits neither checks.json nor the report. No test shows that the implement-terminal lift leaves a registered artifact unlifted. The diff adds only test_named_shakeout_report_is_required_even_when_verification_is_excused. (do instead: Add three tests to tests/test_stages.py through the production pipeline. (1) Verification writes a valid ShakeoutReport to tickets/<stem>/shakeout-report.json; assert the checks commit contains it. (2) Verification writes an invalid report; assert the Check is gate_failed with one `verification` finding and the checks commit holds neither file. (3) The implementer writes a valid report into the outbox; assert the implement commit does not contain it.)
- [acceptance] tests/test_stages.py:306 The first half of acceptance criterion 2 is unmet. No test shows that a report left in the outbox before Check is deleted before Verification runs, so that a Verification that writes nothing lifts no report. (do instead: Add a test that places a valid shakeout-report.json in the worktree outbox before Check, runs a Verification that writes nothing, and asserts the file is not in the checks commit or on main.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4bdfac094390b6b5a38ee32b2a69dab3658d1ae2",
  "stem": "shakeout-report-lane",
  "reviewed_sha": "4bdfac094390b6b5a38ee32b2a69dab3658d1ae2",
  "summary": "The engine changes look plausible, but tests/test_stages.py adds only the report-required test; the tests acceptance criteria 1 and 2 require for lifting and stale-report deletion are missing.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": 306,
      "message": "Acceptance criterion 1 is unmet. No test shows that a Check whose Verification writes a valid shakeout-report.json lifts it in the `chupa(<stem>): checks` commit. No test shows that a schema-invalid report makes the Check gate_failed and commits neither checks.json nor the report. No test shows that the implement-terminal lift leaves a registered artifact unlifted. The diff adds only test_named_shakeout_report_is_required_even_when_verification_is_excused.",
      "paved_road": "Add three tests to tests/test_stages.py through the production pipeline. (1) Verification writes a valid ShakeoutReport to tickets/<stem>/shakeout-report.json; assert the checks commit contains it. (2) Verification writes an invalid report; assert the Check is gate_failed with one `verification` finding and the checks commit holds neither file. (3) The implementer writes a valid report into the outbox; assert the implement commit does not contain it."
    },
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": 306,
      "message": "The first half of acceptance criterion 2 is unmet. No test shows that a report left in the outbox before Check is deleted before Verification runs, so that a Verification that writes nothing lifts no report.",
      "paved_road": "Add a test that places a valid shakeout-report.json in the worktree outbox before Check, runs a Verification that writes nothing, and asserts the file is not in the checks commit or on main."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
