# Review: approve

The diff adds `--extension` to confirm and reject. It sends `actor` from the CLI through the admission request, `settle_admissions` and `apply_verdict` to `verdict_locked`. `verdict_locked` skips only the same-content refusal, the keep signal stays `actor: operator`, and the ticket's tests and doc updates are included inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "782a5ac6020cdfca62334feae8af651a9185756e",
  "stem": "keep-ignores-content",
  "reviewed_sha": "782a5ac6020cdfca62334feae8af651a9185756e",
  "summary": "The diff adds `--extension` to confirm and reject. It sends `actor` from the CLI through the admission request, `settle_admissions` and `apply_verdict` to `verdict_locked`. `verdict_locked` skips only the same-content refusal, the keep signal stays `actor: operator`, and the ticket's tests and doc updates are included inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
