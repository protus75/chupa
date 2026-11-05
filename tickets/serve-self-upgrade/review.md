# Review: approve

The diff meets all six testable criteria. Serve records the engine's chupa/specs trees at startup and re-checks them at admission and merge boundaries; on a change it stops admitting, waits until idle, and hands off in drain's order (journal, cleanup, close, release lock, spawn) with kill-wins checks. One shared reexec_argv builds the argv for both verbs, drain keeps its --parked arguments, and the docs are updated.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "399d2986ad3270ccc354d97597636ea28d1f2bf1",
  "stem": "serve-self-upgrade",
  "reviewed_sha": "399d2986ad3270ccc354d97597636ea28d1f2bf1",
  "summary": "The diff meets all six testable criteria. Serve records the engine's chupa/specs trees at startup and re-checks them at admission and merge boundaries; on a change it stops admitting, waits until idle, and hands off in drain's order (journal, cleanup, close, release lock, spawn) with kill-wins checks. One shared reexec_argv builds the argv for both verbs, drain keeps its --parked arguments, and the docs are updated.",
  "findings": [],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
