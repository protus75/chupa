# Review: snag

The plan-bound hold and release mostly work, but the spec-gap-unresolved check can pick a terminal that has no round record, and the moved machine keep now charges a retry unit to non-plan-bound premise_failed re-offers.

## Findings

- [logic] chupa/runner.py:297 `prior` is the latest lineage terminal that carries `plan_units`. That includes round-less terminals: `spec_gap_unresolved` and `hardening cap spent`. For one of those, `covered` is {} and D is empty, so step (1) is skipped and a new round is filed for units an earlier closed round already covered and left byte-identical. Example: round 1 covers {A, B} and closes `already_satisfied`. The next run ends `spec_gap_unresolved` {A, B}. A commit changes only A, which releases the stem. The re-run gaps only B. P is the unresolved terminal (no `round`), so B is re-hardened and draws a `hardening` unit instead of routing `spec_gap_unresolved`. (do instead: Choose P as the latest lineage terminal that carries a `round` (with its `plan_units`), or carry D's coverage forward. Add a test where an unresolved arrival is released by a change to one bound unit and the remaining unchanged covered unit routes `spec_gap_unresolved` again.)
- [scope] chupa/drain.py:395 The retry draw is now `if queued or (...)`, so every Reject-queue re-offer draws `retry`. That includes non-plan-bound `premise_failed` arrivals (routed via abandon-human), which the old `last != PREMISE` guard re-ran free after a ticket edit. The ticket limits the premise_failed retry draw to plan-bound releases, so this changes accounting for ordinary premise arrivals. (do instead: Draw retry unconditionally only for plan-bound arrivals, e.g. `bound = queued and "plan_units" in reject_queue(history)[stem]`. Keep the existing PREMISE / SPEC_GAP_HOLD exemptions for every other re-offer.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "9e267976598b8ccc837722c051dabe713ff2b335",
  "stem": "plan-bound-reject-release",
  "reviewed_sha": "9e267976598b8ccc837722c051dabe713ff2b335",
  "summary": "The plan-bound hold and release mostly work, but the spec-gap-unresolved check can pick a terminal that has no round record, and the moved machine keep now charges a retry unit to non-plan-bound premise_failed re-offers.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/runner.py",
      "line": 297,
      "message": "`prior` is the latest lineage terminal that carries `plan_units`. That includes round-less terminals: `spec_gap_unresolved` and `hardening cap spent`. For one of those, `covered` is {} and D is empty, so step (1) is skipped and a new round is filed for units an earlier closed round already covered and left byte-identical. Example: round 1 covers {A, B} and closes `already_satisfied`. The next run ends `spec_gap_unresolved` {A, B}. A commit changes only A, which releases the stem. The re-run gaps only B. P is the unresolved terminal (no `round`), so B is re-hardened and draws a `hardening` unit instead of routing `spec_gap_unresolved`.",
      "paved_road": "Choose P as the latest lineage terminal that carries a `round` (with its `plan_units`), or carry D's coverage forward. Add a test where an unresolved arrival is released by a change to one bound unit and the remaining unchanged covered unit routes `spec_gap_unresolved` again.",
      "kind": null,
      "unit": null
    },
    {
      "code": "scope",
      "path": "chupa/drain.py",
      "line": 395,
      "message": "The retry draw is now `if queued or (...)`, so every Reject-queue re-offer draws `retry`. That includes non-plan-bound `premise_failed` arrivals (routed via abandon-human), which the old `last != PREMISE` guard re-ran free after a ticket edit. The ticket limits the premise_failed retry draw to plan-bound releases, so this changes accounting for ordinary premise arrivals.",
      "paved_road": "Draw retry unconditionally only for plan-bound arrivals, e.g. `bound = queued and \"plan_units\" in reject_queue(history)[stem]`. Keep the existing PREMISE / SPEC_GAP_HOLD exemptions for every other re-offer.",
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
