# Review: approve

The diff moves specs/ to chupa/specs/ unchanged, points every loader in scope at the new place with no fallback to the old one, has engine_trees read only HEAD:chupa and the serve_handoff body drop its specs key, updates the inventory in config.yaml, and stays inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "878cbbffb5cba57b586dfdad6e524345303a9481",
  "stem": "specs-move",
  "reviewed_sha": "878cbbffb5cba57b586dfdad6e524345303a9481",
  "summary": "The diff moves specs/ to chupa/specs/ unchanged, points every loader in scope at the new place with no fallback to the old one, has engine_trees read only HEAD:chupa and the serve_handoff body drop its specs key, updates the inventory in config.yaml, and stays inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
