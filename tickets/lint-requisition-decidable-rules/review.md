# Review: approve

The diff adds `lint_findings` with the three allowlist rules, calls it only from intake, `lint`, `new`, and `review_target`, turns a `TicketInvalid` in `review_ticket` into a snag with no model call, trims and bumps the requisition spec, updates the docs, and adds tests for every acceptance criterion while leaving `validate_ticket` and merge/scan admission unchanged.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "148dcfe566aec27244badd48bd7a38f6a9863a8e",
  "stem": "lint-requisition-decidable-rules",
  "reviewed_sha": "148dcfe566aec27244badd48bd7a38f6a9863a8e",
  "summary": "The diff adds `lint_findings` with the three allowlist rules, calls it only from intake, `lint`, `new`, and `review_target`, turns a `TicketInvalid` in `review_ticket` into a snag with no model call, trims and bumps the requisition spec, updates the docs, and adds tests for every acceptance criterion while leaving `validate_ticket` and merge/scan admission unchanged.",
  "findings": [],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
