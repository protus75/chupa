# Review: approve

The diff moves intake's stray rule and per-stem claim, validate, lint and evidence logic into two helpers in `chupa/tickets.py` that run no git and write nothing; intake keeps its lock, its git call order, its refusal message, its stamping, its commits and its journal signal unchanged; the new tests cover every point in acceptance criteria 1 and 2.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1a44609ac42fd210f25ec511f094aece642d739c",
  "stem": "intake-plan-helper",
  "reviewed_sha": "1a44609ac42fd210f25ec511f094aece642d739c",
  "summary": "The diff moves intake's stray rule and per-stem claim, validate, lint and evidence logic into two helpers in `chupa/tickets.py` that run no git and write nothing; intake keeps its lock, its git call order, its refusal message, its stamping, its commits and its journal signal unchanged; the new tests cover every point in acceptance criteria 1 and 2.",
  "findings": [],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
