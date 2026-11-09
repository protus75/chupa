# Review: approve

The diff adds `stale_core`, which reads each routed conduct file committed at HEAD. `serve`, `drain` and `run` call it and refuse before taking the lock. `doctor` gains the `core` row. The required tests and docs are present, and every change is inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "66d3033e1adc24554eccf0d2497ed6eb6ee4e87c",
  "stem": "core-drift-preflight",
  "reviewed_sha": "66d3033e1adc24554eccf0d2497ed6eb6ee4e87c",
  "summary": "The diff adds `stale_core`, which reads each routed conduct file committed at HEAD. `serve`, `drain` and `run` call it and refuse before taking the lock. `doctor` gains the `core` row. The required tests and docs are present, and every change is inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
