# Review: approve

Reconcile now runs the one run-terminal `harvest` for each orphan that has a worktree, through an injected callable. The order is harvest, then the `abandoned` journal entry, then worktree removal. A harvest error only journals a `harvest_failed` signal and the reap continues; an orphan with no worktree is still reaped bare. Both production callers pass the harvest, the tests cover every acceptance criterion, and every changed file is inside the fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f60cc0eb9f8951ec14e1f331ec419ab23863c801",
  "stem": "spine-harvest-orphans",
  "reviewed_sha": "f60cc0eb9f8951ec14e1f331ec419ab23863c801",
  "summary": "Reconcile now runs the one run-terminal `harvest` for each orphan that has a worktree, through an injected callable. The order is harvest, then the `abandoned` journal entry, then worktree removal. A harvest error only journals a `harvest_failed` signal and the reap continues; an orphan with no worktree is still reaped bare. Both production callers pass the harvest, the tests cover every acceptance criterion, and every changed file is inside the fence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
