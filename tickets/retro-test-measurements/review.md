# Review: approve

The diff adds both `Retro` switches. It aggregates per-gate test timing (max seconds and invoice count per slow test) and coverage (latest percent, plus latest, min and run count per file) over the window's Check invoices, in journal order. Each key is absent when its switch is off. The diff adds the required integration and in-memory unit tests, updates both docs and adjusts the status provenance expectation, all within the fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1f7547d5aad3e57126281ba81d571dae2e867e58",
  "stem": "retro-test-measurements",
  "reviewed_sha": "1f7547d5aad3e57126281ba81d571dae2e867e58",
  "summary": "The diff adds both `Retro` switches. It aggregates per-gate test timing (max seconds and invoice count per slow test) and coverage (latest percent, plus latest, min and run count per file) over the window's Check invoices, in journal order. Each key is absent when its switch is off. The diff adds the required integration and in-memory unit tests, updates both docs and adjusts the status provenance expectation, all within the fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
