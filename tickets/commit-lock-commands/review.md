# Review: approve

The diff meets every acceptance criterion and stays inside the scope fence: `_review` no longer takes `chupa.lock` or reaps and instead runs intake under the commit lock, `_verdict` runs intake before publishing to a live engine and refuses on an intake failure or a commit-lock timeout, the snapshot gains `commitLock` through a shared verb rule and makes Review, Confirm and Reject available while an engine runs, `view.js` only draws the two lock fields, and the docs and tests are updated to match.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5b68513e1a9524c582d087690066347b512cd999",
  "stem": "commit-lock-commands",
  "reviewed_sha": "5b68513e1a9524c582d087690066347b512cd999",
  "summary": "The diff meets every acceptance criterion and stays inside the scope fence: `_review` no longer takes `chupa.lock` or reaps and instead runs intake under the commit lock, `_verdict` runs intake before publishing to a live engine and refuses on an intake failure or a commit-lock timeout, the snapshot gains `commitLock` through a shared verb rule and makes Review, Confirm and Reject available while an engine runs, `view.js` only draws the two lock fields, and the docs and tests are updated to match.",
  "findings": [],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
