# Review: approve

All three tests now check that produced_at_sha falls between a HEAD read before the run and one read after it, using Git.merge_base, and they compare the reports with the SHA excluded; the eval modules and git.py are unchanged.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "eccc130c58b1700036b5a097b75af8d7a9885963",
  "stem": "soak-report-head-race",
  "reviewed_sha": "eccc130c58b1700036b5a097b75af8d7a9885963",
  "summary": "All three tests now check that produced_at_sha falls between a HEAD read before the run and one read after it, using Git.merge_base, and they compare the reports with the SHA excluded; the eval modules and git.py are unchanged.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
