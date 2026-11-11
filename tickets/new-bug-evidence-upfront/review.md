# Review: approve

`new --kind bug` now refuses with exit 2 unless `--evidence` names existing, non-symlink files with distinct names, and every refusal comes before any write; `new` copies the evidence byte for byte into `tickets/<stem>/evidence/`, `dev.py` forwards the flag, the tests cover every listed case, and the authoring guide, how-chupa-works and README describe the new flow.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "6caf71ded64f691a4d9acad62db7938da183b6d0",
  "stem": "new-bug-evidence-upfront",
  "reviewed_sha": "6caf71ded64f691a4d9acad62db7938da183b6d0",
  "summary": "`new --kind bug` now refuses with exit 2 unless `--evidence` names existing, non-symlink files with distinct names, and every refusal comes before any write; `new` copies the evidence byte for byte into `tickets/<stem>/evidence/`, `dev.py` forwards the flag, the tests cover every listed case, and the authoring guide, how-chupa-works and README describe the new flow.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
