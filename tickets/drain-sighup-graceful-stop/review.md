# Review: approve

SIGINT, SIGTERM and SIGHUP now reach the drain through a renamed `_engine_signals`. The handler publishes a kill to the control inbox, so the drain uses the existing kill path. The handlers are removed before the lock is released. The diff updates every call site, the off-thread tests, the docs and the regression script, and stays inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4fe10ae72af57f3fa81a27529d192a4c78c3ece7",
  "stem": "drain-sighup-graceful-stop",
  "reviewed_sha": "4fe10ae72af57f3fa81a27529d192a4c78c3ece7",
  "summary": "SIGINT, SIGTERM and SIGHUP now reach the drain through a renamed `_engine_signals`. The handler publishes a kill to the control inbox, so the drain uses the existing kill path. The handlers are removed before the lock is released. The diff updates every call site, the off-thread tests, the docs and the regression script, and stays inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
