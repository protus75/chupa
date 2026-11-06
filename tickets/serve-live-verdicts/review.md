# Review: snag

The live keep path, crash replay, refusal reporting and serve re-offer are implemented and tested, but no test covers acceptance criterion 2: a live `reject` while the lock is held.

## Findings

- [acceptance] tests/test_control.py:416 Criterion 2 is unmet. It requires tests showing that `reject <stem>`, sent while a lock is held, works on a Reject-queue stem and on a committed draft: it stamps `state: rejected`, commits it, journals the `rejected` transition once, and files dead-dependent box messages exactly as the lock-free path does. It names tests/test_control.py and tests/test_control_cli.py as the check. Every added or changed test publishes only `confirm` requests (`test_verdict_inbox_known_unknown_and_crash_replay`, the updated `test_confirm_held_without_writer_lock`, `test_live_keep_reoffers_and_reports_repeat`). Nothing tests the new keyed reject path: `verdict_locked(kill=True, key=...)`, the replay prefix, the keyed recommit block in `reject_ticket`, and the guarded `reject_verdict kill` and `rejected` appends. (do instead: Add tests in tests/test_control.py and/or tests/test_control_cli.py. With the lock held, run `reject` through `entry.main` or publish a null-`hold_id` reject request, then run `settle_admissions` (at least twice, once crashing mid-effect) for a Reject-queue stem and for a committed draft that has a confirmed dependent. Assert the committed `state: rejected`, exactly one `rejected` STATE_TRANSITION, exactly one `reject_verdict kill`, and the same dead-dependency box messages the lock-free `reject` files.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3fe8726215547d325a2bb3a446e894ef792b8fb9",
  "stem": "serve-live-verdicts",
  "reviewed_sha": "3fe8726215547d325a2bb3a446e894ef792b8fb9",
  "summary": "The live keep path, crash replay, refusal reporting and serve re-offer are implemented and tested, but no test covers acceptance criterion 2: a live `reject` while the lock is held.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_control.py",
      "line": 416,
      "message": "Criterion 2 is unmet. It requires tests showing that `reject <stem>`, sent while a lock is held, works on a Reject-queue stem and on a committed draft: it stamps `state: rejected`, commits it, journals the `rejected` transition once, and files dead-dependent box messages exactly as the lock-free path does. It names tests/test_control.py and tests/test_control_cli.py as the check. Every added or changed test publishes only `confirm` requests (`test_verdict_inbox_known_unknown_and_crash_replay`, the updated `test_confirm_held_without_writer_lock`, `test_live_keep_reoffers_and_reports_repeat`). Nothing tests the new keyed reject path: `verdict_locked(kill=True, key=...)`, the replay prefix, the keyed recommit block in `reject_ticket`, and the guarded `reject_verdict kill` and `rejected` appends.",
      "paved_road": "Add tests in tests/test_control.py and/or tests/test_control_cli.py. With the lock held, run `reject` through `entry.main` or publish a null-`hold_id` reject request, then run `settle_admissions` (at least twice, once crashing mid-effect) for a Reject-queue stem and for a committed draft that has a confirmed dependent. Assert the committed `state: rejected`, exactly one `rejected` STATE_TRANSITION, exactly one `reject_verdict kill`, and the same dead-dependency box messages the lock-free `reject` files.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
