# Review: approve

The snapshot now reports chupaReview as "off" for closed or invalid rows, "locked" only when the engine is alive and the row is uncommitted, and "on" otherwise. test_watch.py covers the committed, dirty and stopped cases, and the carried reproducer fails at base and passes on the branch.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a938c75e0751f662aa656f29dc15091f5ca52092",
  "stem": "review-menu-committed-unlocked",
  "reviewed_sha": "a938c75e0751f662aa656f29dc15091f5ca52092",
  "summary": "The snapshot now reports chupaReview as \"off\" for closed or invalid rows, \"locked\" only when the engine is alive and the row is uncommitted, and \"on\" otherwise. test_watch.py covers the committed, dirty and stopped cases, and the carried reproducer fails at base and passes on the branch.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
