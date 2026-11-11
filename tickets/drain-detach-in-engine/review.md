# Review: approve

`chupa drain --detach` now handles the detach inside the engine through `seams.spawn_detached`, and it runs right after `load_config` with a child argv that has no `--detach`; `dev.py` and both extension drain launches only forward argv from the snapshot; the docs, both rule files and the tests all match the ticket.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "64a544ae1e0333637e28f55567ec5576f304a73a",
  "stem": "drain-detach-in-engine",
  "reviewed_sha": "64a544ae1e0333637e28f55567ec5576f304a73a",
  "summary": "`chupa drain --detach` now handles the detach inside the engine through `seams.spawn_detached`, and it runs right after `load_config` with a child argv that has no `--detach`; `dev.py` and both extension drain launches only forward argv from the snapshot; the docs, both rule files and the tests all match the ticket.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
