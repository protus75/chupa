# Review: approve

The diff adds a `badge` field to the snapshot. It is set only when the engine is alive and the queued plus running count is above zero. The extension sets `stepsView.badge` from that field without computing anything itself, removes the visibility gate and the `views` list, refreshes once in `activate`, and adds the tests and the docs sentence the ticket asks for.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "48db3f9f54771c2f3b125224848a49834fef4b43",
  "stem": "vscode-activity-badge",
  "reviewed_sha": "48db3f9f54771c2f3b125224848a49834fef4b43",
  "summary": "The diff adds a `badge` field to the snapshot. It is set only when the engine is alive and the queued plus running count is above zero. The extension sets `stepsView.badge` from that field without computing anything itself, removes the visibility gate and the `views` list, refreshes once in `activate`, and adds the tests and the docs sentence the ticket asks for.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
