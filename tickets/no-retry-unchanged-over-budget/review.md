# Review: approve

The diff adds `budget_parked` and uses it in the drain's held set, in `_between_tickets` and in the scheduler hold. It reports the diff-budget road only when no cap is spent, so the prior finding is resolved. `premise_parked` is unchanged, other gate failures are still re-offered, the docs are updated, and the required tests are present.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "d2342d3bb6e0903b814b272b8ec31bd01325cc36",
  "stem": "no-retry-unchanged-over-budget",
  "reviewed_sha": "d2342d3bb6e0903b814b272b8ec31bd01325cc36",
  "summary": "The diff adds `budget_parked` and uses it in the drain's held set, in `_between_tickets` and in the scheduler hold. It reports the diff-budget road only when no cap is spent, so the prior finding is resolved. `premise_parked` is unchanged, other gate failures are still re-offered, the docs are updated, and the required tests are present.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
