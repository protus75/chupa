# Review: snag

The fifth failure can leave a stem unrouted on the direct merge-result path, so the daemon can re-dispatch it and let it fail a sixth time.

## Findings

- [logic] chupa/runner.py:300 The attempts override in `failure_terminal` is skipped whenever `rework_requested and reworked.outcome == "ok"`, not only for a split that retires the parent. `TicketWriter.consume_result` reaches this through `consume_handoff`, which bypasses the new `drive` pre-check. With 4 prior failures, `spent` is None, so `apply_rework` runs. An `update` then journals the 5th `gate_failed` with `dispatch: retry` and no `routed`; an ok `escalate` also journals it unrouted, with `dispatch: escalate` or `reject_queue`. The new guards are only in the drain's `_select` and `_settle`. The daemon `Scheduler.dispatch_next` holds only stems in `reject_queue(events)` and never checks `spent`. The watcher republishes the updated ticket, so the stem is dispatched again. Implement makes a model call, and a failure there is a 6th failure in the lineage, which the ticket's Definition of rejected forbids. `test_attempts_cap_preserves_published_rework_on_direct_merge_result` pins this for `update` by asserting `ticket.stem not in reject_queue(events)` at 5 draws. (do instead: Limit the exemption to a published split, which still retires its parent. For every other outcome, including a published `update` or ok `escalate`, set the reason to `attempts cap spent` and journal `dispatch` and `routed` as `reject_queue`, leaving the published ticket text in place. Change the `update` case of the test to assert that the stem is in the Reject queue with that reason, and update the how-chupa-works.md section 6.4 note to match.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "6001420e5a860272e0f0a6752c398380f6c6f539",
  "stem": "attempts-cap",
  "reviewed_sha": "6001420e5a860272e0f0a6752c398380f6c6f539",
  "summary": "The fifth failure can leave a stem unrouted on the direct merge-result path, so the daemon can re-dispatch it and let it fail a sixth time.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/runner.py",
      "line": 300,
      "message": "The attempts override in `failure_terminal` is skipped whenever `rework_requested and reworked.outcome == \"ok\"`, not only for a split that retires the parent. `TicketWriter.consume_result` reaches this through `consume_handoff`, which bypasses the new `drive` pre-check. With 4 prior failures, `spent` is None, so `apply_rework` runs. An `update` then journals the 5th `gate_failed` with `dispatch: retry` and no `routed`; an ok `escalate` also journals it unrouted, with `dispatch: escalate` or `reject_queue`. The new guards are only in the drain's `_select` and `_settle`. The daemon `Scheduler.dispatch_next` holds only stems in `reject_queue(events)` and never checks `spent`. The watcher republishes the updated ticket, so the stem is dispatched again. Implement makes a model call, and a failure there is a 6th failure in the lineage, which the ticket's Definition of rejected forbids. `test_attempts_cap_preserves_published_rework_on_direct_merge_result` pins this for `update` by asserting `ticket.stem not in reject_queue(events)` at 5 draws.",
      "paved_road": "Limit the exemption to a published split, which still retires its parent. For every other outcome, including a published `update` or ok `escalate`, set the reason to `attempts cap spent` and journal `dispatch` and `routed` as `reject_queue`, leaving the published ticket text in place. Change the `update` case of the test to assert that the stem is in the Reject queue with that reason, and update the how-chupa-works.md section 6.4 note to match.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
