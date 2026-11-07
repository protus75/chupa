# Review: approve

The diff replaces the duplicated premise and diff-budget park predicates with a single `parked_blob` function. Drain, serve, snapshot and `queue` all use it with their old hold semantics unchanged, and the tests, reproducer and doc the ticket requires are included.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "8a9270655d2a26301cd802011aaf93d7dc6d2a94",
  "stem": "shared-hold-rule",
  "reviewed_sha": "8a9270655d2a26301cd802011aaf93d7dc6d2a94",
  "summary": "The diff replaces the duplicated premise and diff-budget park predicates with a single `parked_blob` function. Drain, serve, snapshot and `queue` all use it with their old hold semantics unchanged, and the tests, reproducer and doc the ticket requires are included.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
