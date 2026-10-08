# Review: approve

The copy check runs after the SPEC DEPTH check and before validate_ticket, only inside seed review; it skips cited ids that do not resolve, normalizes whitespace on both sides, leaves out the Plan contract section, snags 60+ character copies with the required kind, paved road and mechanical tag before any requisition_review call, and the tests cover the copied, short, uncited and Plan-contract-placement cases.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e77b9d98eb6336e497d80b9e9aae71da976684bc",
  "stem": "seed-copy-refusal",
  "reviewed_sha": "e77b9d98eb6336e497d80b9e9aae71da976684bc",
  "summary": "The copy check runs after the SPEC DEPTH check and before validate_ticket, only inside seed review; it skips cited ids that do not resolve, normalizes whitespace on both sides, leaves out the Plan contract section, snags 60+ character copies with the required kind, paved road and mechanical tag before any requisition_review call, and the tests cover the copied, short, uncited and Plan-contract-placement cases.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
