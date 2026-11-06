# Review: approve

Rework's review closure journals a requisition_verdict approve record with the same body keys as author.py, keyed to the proposal stem, only for approve verdicts; the new test covers the snag case (no records) and checks that each approved proposal's ticket_sha equals its blob sha.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "56ae9e1436340e732dd6191681563fc833fba7b4",
  "stem": "review-approval-records",
  "reviewed_sha": "56ae9e1436340e732dd6191681563fc833fba7b4",
  "summary": "Rework's review closure journals a requisition_verdict approve record with the same body keys as author.py, keyed to the proposal stem, only for approve verdicts; the new test covers the snag case (no records) and checks that each approved proposal's ticket_sha equals its blob sha.",
  "findings": [],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
