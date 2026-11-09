# Review: approve

One helper, _base_worktree, now does all base-worktree setup in chupa/stages.py, with the assert, path, stale removal, mkdir, detached add, and return in the order the ticket asks. All three call sites call it and keep their try/finally blocks unchanged, and the new test fails for a helper that skips the stale-worktree removal.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "78684bea246a868a34277d2f1581488f79bd9c5b",
  "stem": "stages-base-worktree-helper",
  "reviewed_sha": "78684bea246a868a34277d2f1581488f79bd9c5b",
  "summary": "One helper, _base_worktree, now does all base-worktree setup in chupa/stages.py, with the assert, path, stale removal, mkdir, detached add, and return in the order the ticket asks. All three call sites call it and keep their try/finally blocks unchanged, and the new test fails for a helper that skips the stale-worktree removal.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
