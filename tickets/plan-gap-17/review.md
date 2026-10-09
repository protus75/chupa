# Review: approve

The diff changes only the fenced 19.P4.provider-cooldown-failover unit and states both gap facts. The first is a deterministic production projection built from shared Thresh occupancy and the existing runner.call_timeout. The second is a session-scoped auth-exclusion rule, released by a fresh successful startup preflight, that keeps the merged breaker's auth_error streak reset and null open_until. Neither fact contradicts merged thresh.py or runner.py.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0895989cd196ad5ab204ee0a3b727d2d3fb5d5aa",
  "stem": "plan-gap-17",
  "reviewed_sha": "0895989cd196ad5ab204ee0a3b727d2d3fb5d5aa",
  "summary": "The diff changes only the fenced 19.P4.provider-cooldown-failover unit and states both gap facts. The first is a deterministic production projection built from shared Thresh occupancy and the existing runner.call_timeout. The second is a session-scoped auth-exclusion rule, released by a fresh successful startup preflight, that keeps the merged breaker's auth_error streak reset and null open_until. Neither fact contradicts merged thresh.py or runner.py.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
