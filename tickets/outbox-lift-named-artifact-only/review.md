# Review: approve

The diff adds the pure `_lift_decision` predicate and `LIFT_MAX_BYTES`, and `_lift_files` now lifts only each kind's named artifact, never a symlink, and raises ArtifactInvalid for a file over 256 KB. The four named unit tests, the three outbox_lift integration tests and the section 3.3 doc sentence match the ticket, and every change stays inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "aa4167fc2259abd6919ed1e1a1f44cd156de6623",
  "stem": "outbox-lift-named-artifact-only",
  "reviewed_sha": "aa4167fc2259abd6919ed1e1a1f44cd156de6623",
  "summary": "The diff adds the pure `_lift_decision` predicate and `LIFT_MAX_BYTES`, and `_lift_files` now lifts only each kind's named artifact, never a symlink, and raises ArtifactInvalid for a file over 256 KB. The four named unit tests, the three outbox_lift integration tests and the section 3.3 doc sentence match the ticket, and every change stays inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
