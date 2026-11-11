# Review: approve

The diff adds `runner.reap` and calls it after the writer lock is taken in `verdict`, `_review` (dirty path), dismiss, triage and `_retro`. `_order`, the status projection and render, and the observe Reject flag now treat a dead `running` stem as interrupted through `reconcile.orphans` and `lock_holder`, and a run held for a merge regate stays in flight. The required tests, the reproducer and the doc edits are present, and the prior review's disk and wall-clock findings in `test_status_verb_passes_alive` are fixed with a faked `SPECS_DIR`, a faked `load_spec` and a fixed clock.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "67d299942e951d24892e4ab20bdc91287feddc3c",
  "stem": "stale-running-after-kill",
  "reviewed_sha": "67d299942e951d24892e4ab20bdc91287feddc3c",
  "summary": "The diff adds `runner.reap` and calls it after the writer lock is taken in `verdict`, `_review` (dirty path), dismiss, triage and `_retro`. `_order`, the status projection and render, and the observe Reject flag now treat a dead `running` stem as interrupted through `reconcile.orphans` and `lock_holder`, and a run held for a merge regate stays in flight. The required tests, the reproducer and the doc edits are present, and the prior review's disk and wall-clock findings in `test_status_verb_passes_alive` are fixed with a faked `SPECS_DIR`, a faked `load_spec` and a fixed clock.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
