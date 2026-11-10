# Review: approve

The diff swaps the `owner.published` spy for a check against the ticket parsed from the member checkout's file on disk. It also holds back publication of the corrected `unresolved` ticket until after its attempt-1 offer and asserts that the hold happened, with every change inside the fenced test file.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "aa3c7f56405be79ecee8054a86557487399b9727",
  "stem": "soak-test-publication-race",
  "reviewed_sha": "aa3c7f56405be79ecee8054a86557487399b9727",
  "summary": "The diff swaps the `owner.published` spy for a check against the ticket parsed from the member checkout's file on disk. It also holds back publication of the corrected `unresolved` ticket until after its attempt-1 offer and asserts that the hold happened, with every change inside the fenced test file.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
