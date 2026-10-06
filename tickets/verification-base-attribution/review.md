# Review: snag

The base attribution is wired correctly in stages.py and git.py, but the base-red drain re-entry test required by AC5 is missing, and the existing branch-only-red re-entry test was changed even though the ticket says it must stay as is.

## Findings

- [acceptance] tests/test_drain_reentry.py:70 AC5 and Scope-in require a new base-red case in tests/test_drain_reentry.py. In it, a command red at both base and branch lets the drain merge the ticket in one attempt with no `retry` draw, and exactly one `failure_report` names the command. The diff adds no such test. The file still holds only its three existing tests, and the drain-level guarantee in 'Definition of rejected' (a base-red command never draws `retry`) is untested. (do instead: Add a test to tests/test_drain_reentry.py: Verification red on main and on the branch, drain with a single implement+verdict script, assert exit 0, one implement request, no `retry` dispatch in the journal transitions, and one box `failure_report` with outcome `base_red` whose summary names the command.)
- [acceptance] tests/test_drain_reentry.py:72 AC5 says the existing branch-only-red re-entry test stays unchanged. The diff rewrites `test_a_reoffer_after_a_red_check_renders_the_failing_checks`: it adds a green-base commit and changes the final agent payload. It also rewrites `test_a_stale_review_md_never_feeds_a_later_check_failure`. AC6 permits fixture conversion only in test_diagnose.py and test_terminal.py, so this file has no such permission. (do instead: Leave the existing re-entry tests as they are. If they can only stay red-on-branch-only by changing the shared fixture, make that change in the `author`/`drain` helper or repo fixture so the test bodies stay unchanged. If that is impossible, the ticket must be amended instead of editing the tests silently.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "66c35bd422b8fbcb8d3176d2c6126643675de743",
  "stem": "verification-base-attribution",
  "reviewed_sha": "66c35bd422b8fbcb8d3176d2c6126643675de743",
  "summary": "The base attribution is wired correctly in stages.py and git.py, but the base-red drain re-entry test required by AC5 is missing, and the existing branch-only-red re-entry test was changed even though the ticket says it must stay as is.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_drain_reentry.py",
      "line": 70,
      "message": "AC5 and Scope-in require a new base-red case in tests/test_drain_reentry.py. In it, a command red at both base and branch lets the drain merge the ticket in one attempt with no `retry` draw, and exactly one `failure_report` names the command. The diff adds no such test. The file still holds only its three existing tests, and the drain-level guarantee in 'Definition of rejected' (a base-red command never draws `retry`) is untested.",
      "paved_road": "Add a test to tests/test_drain_reentry.py: Verification red on main and on the branch, drain with a single implement+verdict script, assert exit 0, one implement request, no `retry` dispatch in the journal transitions, and one box `failure_report` with outcome `base_red` whose summary names the command."
    },
    {
      "code": "acceptance",
      "path": "tests/test_drain_reentry.py",
      "line": 72,
      "message": "AC5 says the existing branch-only-red re-entry test stays unchanged. The diff rewrites `test_a_reoffer_after_a_red_check_renders_the_failing_checks`: it adds a green-base commit and changes the final agent payload. It also rewrites `test_a_stale_review_md_never_feeds_a_later_check_failure`. AC6 permits fixture conversion only in test_diagnose.py and test_terminal.py, so this file has no such permission.",
      "paved_road": "Leave the existing re-entry tests as they are. If they can only stay red-on-branch-only by changing the shared fixture, make that change in the `author`/`drain` helper or repo fixture so the test bodies stay unchanged. If that is impossible, the ticket must be amended instead of editing the tests silently."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
