# Review: approve

The diff meets the ticket. Retro now always embeds the measurements. When the embedded prompt would exceed the 0.75 headroom, it writes the whole ordered window as JSONL to the retro call's own spool and gives the model that path instead. A failure now stops suppressing the window once a later merge lands, in both Retro and the CLI verb. The failure signal's key and body are unchanged. The tests and spec version updates match the scope.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a05e4da6fb44359189a616dfa226159aaf5235fa",
  "stem": "retro-window-bound",
  "reviewed_sha": "a05e4da6fb44359189a616dfa226159aaf5235fa",
  "summary": "The diff meets the ticket. Retro now always embeds the measurements. When the embedded prompt would exceed the 0.75 headroom, it writes the whole ordered window as JSONL to the retro call's own spool and gives the model that path instead. A failure now stops suppressing the window once a later merge lands, in both Retro and the CLI verb. The failure signal's key and body are unchanged. The tests and spec version updates match the scope.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
