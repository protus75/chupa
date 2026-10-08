# Review: approve

The diff adds a per-call EventConsumer. Each stdout line is delivered synchronously at the SubprocessExec seam (incomplete chunks and the EOF tail included), parsed with the same `_events` used for the final capture, and scrubbed recursively, keys included, before delivery. Spool capture and results are unchanged. The callback kwargs are omitted when no consumer is given, so production stays dormant. Readers are cancelled and drained on every exceptional unwind before the group kill. The five named obligations are tested through the real process-group seam for both provider shapes, and the edits stay inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "fe09b834381120b060d215408a8e2ed130cd7a08",
  "stem": "watchdog-event-stream",
  "reviewed_sha": "fe09b834381120b060d215408a8e2ed130cd7a08",
  "summary": "The diff adds a per-call EventConsumer. Each stdout line is delivered synchronously at the SubprocessExec seam (incomplete chunks and the EOF tail included), parsed with the same `_events` used for the final capture, and scrubbed recursively, keys included, before delivery. Spool capture and results are unchanged. The callback kwargs are omitted when no consumer is given, so production stays dormant. Readers are cancelled and drained on every exceptional unwind before the group kill. The five named obligations are tested through the real process-group seam for both provider shapes, and the edits stay inside the scope fence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
