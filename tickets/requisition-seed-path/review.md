# Review: approve

The diff meets every acceptance criterion and stays inside the fence: seeding detection uses the `tickets` fence entry, each seed is reviewed on its own with the specified llm keys, any non-approve blocks the whole batch, approved seeds land through one keyed ticket-plane commit with per-seed `ticket_intake` journal events, own seeds re-written byte-identically are skipped on a re-run, a rewritten foreign stem fails, and the merge gate re-checks recorded `ticket_sha` and lint without calling the model again.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4f89048d055ddcb315bb89c71f6425f137d8b36e",
  "stem": "requisition-seed-path",
  "reviewed_sha": "4f89048d055ddcb315bb89c71f6425f137d8b36e",
  "summary": "The diff meets every acceptance criterion and stays inside the fence: seeding detection uses the `tickets` fence entry, each seed is reviewed on its own with the specified llm keys, any non-approve blocks the whole batch, approved seeds land through one keyed ticket-plane commit with per-seed `ticket_intake` journal events, own seeds re-written byte-identically are skipped on a re-run, a rewritten foreign stem fails, and the merge gate re-checks recorded `ticket_sha` and lint without calling the model again.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
