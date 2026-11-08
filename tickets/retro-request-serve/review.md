# Review: approve

The diff meets every acceptance criterion. Serve blocks admission while a retro request or due automatic retro is pending, runs one retro under mutations once upgrade_idle holds, aborts it on kill, and lets a pending stop win. It checks thresholds only after a ticket reaches a terminal state, and the docs are updated. The rewritten tests fix both prior findings: the mock commits retro/1 so the window resets, and the helper waits for idle plus several polls before asserting the exact call list and that no retro is pending.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e482a4f5d394c945126c615516470b20f4c38148",
  "stem": "retro-request-serve",
  "reviewed_sha": "e482a4f5d394c945126c615516470b20f4c38148",
  "summary": "The diff meets every acceptance criterion. Serve blocks admission while a retro request or due automatic retro is pending, runs one retro under mutations once upgrade_idle holds, aborts it on kill, and lets a pending stop win. It checks thresholds only after a ticket reaches a terminal state, and the docs are updated. The rewritten tests fix both prior findings: the mock commits retro/1 so the window resets, and the helper waits for idle plus several polls before asserting the exact call list and that no retro is pending.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
