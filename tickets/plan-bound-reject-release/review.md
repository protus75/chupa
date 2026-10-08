# Review: snag

The plan-bound release path works for `reject_queue`-routed terminals, but a spec-gap hold terminal that became a Reject arrival is released by a machine keep and re-runs without drawing a `retry` unit.

## Findings

- [logic] chupa/drain.py:382 A spec-gap hold terminal carries `plan_units` along with `dispatch: spec_gap_hold`. When any cap is spent, `_settle` journals a `reject_arrival` for it, which makes it a plan-bound Reject arrival. Example: `diagnosis` is spent, `retry` is not, and the hardener's merge changed a bound unit. `_select` then releases the stem and `_dispatch` journals the machine-actor keep. The draw is still skipped because `body.get("dispatch") == SPEC_GAP_HOLD`. The stem re-runs from the Reject queue for free, despite a spent cap. The ticket's Definition of rejected forbids this: a machine release that draws no `retry` unit. (do instead: Let the free re-run apply only to a released hold that was not taken out of the Reject queue. Set a flag when `_dispatch` journals the machine keep (the stem is in `reject_queue`) and always draw one `retry` unit in that case, whatever `dispatch` says. Add a drain test with a spent non-retry cap on a `spec_gap_hold` terminal whose bound unit changes, and assert exactly one `retry` draw.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3d8cb44cb9214ee89880f133b734da8f07df82c5",
  "stem": "plan-bound-reject-release",
  "reviewed_sha": "3d8cb44cb9214ee89880f133b734da8f07df82c5",
  "summary": "The plan-bound release path works for `reject_queue`-routed terminals, but a spec-gap hold terminal that became a Reject arrival is released by a machine keep and re-runs without drawing a `retry` unit.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/drain.py",
      "line": 382,
      "message": "A spec-gap hold terminal carries `plan_units` along with `dispatch: spec_gap_hold`. When any cap is spent, `_settle` journals a `reject_arrival` for it, which makes it a plan-bound Reject arrival. Example: `diagnosis` is spent, `retry` is not, and the hardener's merge changed a bound unit. `_select` then releases the stem and `_dispatch` journals the machine-actor keep. The draw is still skipped because `body.get(\"dispatch\") == SPEC_GAP_HOLD`. The stem re-runs from the Reject queue for free, despite a spent cap. The ticket's Definition of rejected forbids this: a machine release that draws no `retry` unit.",
      "paved_road": "Let the free re-run apply only to a released hold that was not taken out of the Reject queue. Set a flag when `_dispatch` journals the machine keep (the stem is in `reject_queue`) and always draw one `retry` unit in that case, whatever `dispatch` says. Add a drain test with a spent non-retry cap on a `spec_gap_hold` terminal whose bound unit changes, and assert exactly one `retry` draw.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
