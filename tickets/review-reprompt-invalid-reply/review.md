# Review: approve

review_ticket now re-asks on an invalid reply up to driver.retry_cap times, and each re-ask gets its own call_seq; RequisitionVerdict.calls lets rework.py and author.py move past the call_seqs a review used, so key values stay the same when no review re-asks, and the required tests are added or updated.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "7674c09f956916aea56c2f102518b42e4f6e4c59",
  "stem": "review-reprompt-invalid-reply",
  "reviewed_sha": "7674c09f956916aea56c2f102518b42e4f6e4c59",
  "summary": "review_ticket now re-asks on an invalid reply up to driver.retry_cap times, and each re-ask gets its own call_seq; RequisitionVerdict.calls lets rework.py and author.py move past the call_seqs a review used, so key values stay the same when no review re-asks, and the required tests are added or updated.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
