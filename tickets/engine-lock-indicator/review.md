# Review: approve

The diff adds the `lock` snapshot field the ticket asks for, using `processes(ctx)` and `clock()`, and the header now shows a padlock with `snap.lock` or `unlocked` as its tooltip; `engine` is unchanged, the four test cases are present and use fakes, and every change is inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "cee552c77a7b1ca8e65c53683b56618e0652dd02",
  "stem": "engine-lock-indicator",
  "reviewed_sha": "cee552c77a7b1ca8e65c53683b56618e0652dd02",
  "summary": "The diff adds the `lock` snapshot field the ticket asks for, using `processes(ctx)` and `clock()`, and the header now shows a padlock with `snap.lock` or `unlocked` as its tooltip; `engine` is unchanged, the four test cases are present and use fakes, and every change is inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
