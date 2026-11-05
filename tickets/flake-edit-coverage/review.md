# Review: approve

The diff adds the `coverage` field and refuses it at config load when `results` is missing, finds changed lines and pure-deletion neighbors by walking hunk bodies, fails closed on a missing or context-less report only when a flaky test needs classifying, and updates both docs and the tests for each acceptance criterion.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "59cf2aeb7b2d92bedcbe4764b21aa114b8f4b150",
  "stem": "flake-edit-coverage",
  "reviewed_sha": "59cf2aeb7b2d92bedcbe4764b21aa114b8f4b150",
  "summary": "The diff adds the `coverage` field and refuses it at config load when `results` is missing, finds changed lines and pure-deletion neighbors by walking hunk bodies, fails closed on a missing or context-less report only when a flaky test needs classifying, and updates both docs and the tests for each acceptance criterion.",
  "findings": [],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
