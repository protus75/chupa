# Review: approve

The parent now passes its deadline to the child as `--deadline <render_ts>` on the handoff argv, placed before `--stop-lifecycle`, and the child's `_Drain` uses that deadline when it is given; the new integration test, the unit tests, the reproducer and the docs sentence match the ticket and stay inside the fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0469449673d6f62a1fb584169b437f53bd0b6614",
  "stem": "drain-ceiling-carried-on-handoff",
  "reviewed_sha": "0469449673d6f62a1fb584169b437f53bd0b6614",
  "summary": "The parent now passes its deadline to the child as `--deadline <render_ts>` on the handoff argv, placed before `--stop-lifecycle`, and the child's `_Drain` uses that deadline when it is given; the new integration test, the unit tests, the reproducer and the docs sentence match the ticket and stay inside the fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
