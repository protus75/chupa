---
id: tombstone-box-000208-4fc9e397
kind: tombstone
link: declined-box-000031-1edcaff5
reopen_after_days: 90
---
The type `StageResult.artifact: Artifact | None` does not fit the Author stage, because a ticket lacks the base `Artifact` provenance fields. The note asks the plan to choose between two fixes: make `Artifact` a field-less root class with a provenance subclass, or widen `StageResult.artifact` to `BaseModel`.

Registry record declined-box-000031-1edcaff5 already settled this same note: the same `StageResult.artifact` typing mismatch for the Author stage's ticket, with the same two proposed fixes. This message repeats it in different words.

- declined-box-000031-1edcaff5 describes the same mismatch: `StageResult.artifact: Artifact | None` against a ticket that has no base `Artifact` fields
- Both messages offer the same two fixes: a field-less root `Artifact` with a provenance subclass, or widening to `BaseModel`
- The message comes from bootstrap-ingest, the same source as the earlier duplicate notes that were tombstoned (000194-000207)

Message: box-000208-4fc9e397
