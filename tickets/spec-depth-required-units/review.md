# Review: approve

The diff adds `required_units` (the seed's own non-exit entry plus cited registry entries, deduplicated and in order), makes `hardenable_units` build on it with an unchanged result, and switches only the seed-path SPEC DEPTH check to it; the two new tests pin the behavior, and the regression test would fail on the merge base, where `hardenable_units` would gap the uncited P4 rows `missing` and `lookahead`.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "2501313b506458bcf45f9174a7dba7cb97b23fda",
  "stem": "spec-depth-required-units",
  "reviewed_sha": "2501313b506458bcf45f9174a7dba7cb97b23fda",
  "summary": "The diff adds `required_units` (the seed's own non-exit entry plus cited registry entries, deduplicated and in order), makes `hardenable_units` build on it with an unchanged result, and switches only the seed-path SPEC DEPTH check to it; the two new tests pin the behavior, and the regression test would fail on the merge base, where `hardenable_units` would gap the uncited P4 rows `missing` and `lookahead`.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
