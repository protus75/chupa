# Review: snag

The serve.py logic matches the ticket, but the shared retro test helper checks call counts the moment bb settles, so the automatic test can flake and the failed-retro test cannot detect a re-blocking retro.

## Findings

- [logic] tests/integration/test_serve.py:2119 In 'automatic' mode, every_merges: 1 is still due after bb merges, because the mocked Retro commits no report and the window never resets. Serve's check_retro after bb therefore sets retro_due and runs a second forced=False retro at the next idle point. The final `assert calls == [False]` runs right after `terminals(rig, 'bb')` appears and races that second call. The mocked retro's own `assert not any(... bb ... running ...)` also fails on that second call, and run_retro re-raises it through serve. Whether the test passes depends on poll timing. (do instead: Make the outcome deterministic. Either have the automatic-mode mock journal what a committed report would, so the window resets, or wait until serve is idle after bb (no writers, a few polls elapsed) and assert the exact expected call list. Keep the bb-not-running assertion only for the first call.)
- [logic] tests/integration/test_serve.py:2119 test_failed_retro_does_not_reblock cannot fail on the defect it is meant to rule out. The only point where a suppressed window could come due again is after bb settles, and the helper asserts `calls == [False]` as soon as bb reaches a terminal state, before serve's next loop could run a second retro. If the suppressing_failure check were removed from check_retro, serve would run the retro again (and block admission) after bb, but this assertion would usually still pass. Acceptance criterion 5 ('not run again for the same window') is therefore not demonstrated. (do instead: In 'failed' mode, after bb settles, wait until serve reaches an idle point (for example, until rig.owner.upgrade_idle() holds and several SERVE_POLL_S polls have passed). Then assert calls == [False] and that rig.owner.retro_pending() is False, so a re-blocking retro would make the test fail.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "2e05ed65bb10a31d1a2f439aff678e25110f6f86",
  "stem": "retro-request-serve",
  "reviewed_sha": "2e05ed65bb10a31d1a2f439aff678e25110f6f86",
  "summary": "The serve.py logic matches the ticket, but the shared retro test helper checks call counts the moment bb settles, so the automatic test can flake and the failed-retro test cannot detect a re-blocking retro.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/integration/test_serve.py",
      "line": 2119,
      "message": "In 'automatic' mode, every_merges: 1 is still due after bb merges, because the mocked Retro commits no report and the window never resets. Serve's check_retro after bb therefore sets retro_due and runs a second forced=False retro at the next idle point. The final `assert calls == [False]` runs right after `terminals(rig, 'bb')` appears and races that second call. The mocked retro's own `assert not any(... bb ... running ...)` also fails on that second call, and run_retro re-raises it through serve. Whether the test passes depends on poll timing.",
      "paved_road": "Make the outcome deterministic. Either have the automatic-mode mock journal what a committed report would, so the window resets, or wait until serve is idle after bb (no writers, a few polls elapsed) and assert the exact expected call list. Keep the bb-not-running assertion only for the first call.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/integration/test_serve.py",
      "line": 2119,
      "message": "test_failed_retro_does_not_reblock cannot fail on the defect it is meant to rule out. The only point where a suppressed window could come due again is after bb settles, and the helper asserts `calls == [False]` as soon as bb reaches a terminal state, before serve's next loop could run a second retro. If the suppressing_failure check were removed from check_retro, serve would run the retro again (and block admission) after bb, but this assertion would usually still pass. Acceptance criterion 5 ('not run again for the same window') is therefore not demonstrated.",
      "paved_road": "In 'failed' mode, after bb settles, wait until serve reaches an idle point (for example, until rig.owner.upgrade_idle() holds and several SERVE_POLL_S polls have passed). Then assert calls == [False] and that rig.owner.retro_pending() is False, so a re-blocking retro would make the test fail.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
