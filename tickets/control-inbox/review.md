# Review: approve

The diff meets the ticket: all named tests are present; the identity-bound inbox validates requests fail-closed; publication is durable and never overwrites (link-based, with file and directory fsync); the decision is journaled before application; the journal fold derives exactly-once decisions and an idempotent projection; and dormancy probes are calibrated, all within the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "7d887bf64716bf01fbfd070613faf91b0d8fa025",
  "stem": "control-inbox",
  "reviewed_sha": "7d887bf64716bf01fbfd070613faf91b0d8fa025",
  "summary": "The diff meets the ticket: all named tests are present; the identity-bound inbox validates requests fail-closed; publication is durable and never overwrites (link-based, with file and directory fsync); the decision is journaled before application; the journal fold derives exactly-once decisions and an idempotent projection; and dormancy probes are calibrated, all within the scope fence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
