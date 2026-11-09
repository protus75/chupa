# Review: approve

run_ticket writes engine_start/engine_stop with verb="run" to engine.log the same way drain does. recent_steps now flags engine_lost when the live lock holder's pid differs from the newest engine_start pid. The tests cover the merged run path and both the matching-pid and different-pid holder cases, the docs row names run, and every changed file is inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a96d892bac955cf3772bf544939a1330fe73c322",
  "stem": "run-lifecycle-steps",
  "reviewed_sha": "a96d892bac955cf3772bf544939a1330fe73c322",
  "summary": "run_ticket writes engine_start/engine_stop with verb=\"run\" to engine.log the same way drain does. recent_steps now flags engine_lost when the live lock holder's pid differs from the newest engine_start pid. The tests cover the merged run path and both the matching-pid and different-pid holder cases, the docs row names run, and every changed file is inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
