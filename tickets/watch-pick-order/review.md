# Review: approve

The diff meets every acceptance criterion. One helper beside `order_tickets` writes `queue.json` atomically through `LocalFileSystem.write`, and both pickers call it right after ordering. `watch.py` stays stdlib-only and shows the recorded order with `runs before:` hints, then the remaining tickets, and falls back to the old listing when the file is missing. Tests and docs sections 7.1 and 10.1 are updated.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "79e5479e9835c737806a7e78b96fce90cac2a733",
  "stem": "watch-pick-order",
  "reviewed_sha": "79e5479e9835c737806a7e78b96fce90cac2a733",
  "summary": "The diff meets every acceptance criterion. One helper beside `order_tickets` writes `queue.json` atomically through `LocalFileSystem.write`, and both pickers call it right after ordering. `watch.py` stays stdlib-only and shows the recorded order with `runs before:` hints, then the remaining tickets, and falls back to the old listing when the file is missing. Tests and docs sections 7.1 and 10.1 are updated.",
  "findings": [],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
