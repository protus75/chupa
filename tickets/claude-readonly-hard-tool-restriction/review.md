# Review: approve

The read-only Claude grant becomes `--tools Read Grep Glob LS --permission-mode dontAsk`, the writes grant is unchanged, the fixture binary accepts only the two current grants, and the tests pin the new grant and rule out `--allowedTools` and `bypassPermissions`; no doc under docs/ or README.md describes the old grant (only the frozen CHUPA_PLAN.md does).

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5364be55a83f9964265d18ea1d6214fe0aeb2774",
  "stem": "claude-readonly-hard-tool-restriction",
  "reviewed_sha": "5364be55a83f9964265d18ea1d6214fe0aeb2774",
  "summary": "The read-only Claude grant becomes `--tools Read Grep Glob LS --permission-mode dontAsk`, the writes grant is unchanged, the fixture binary accepts only the two current grants, and the tests pin the new grant and rule out `--allowedTools` and `bypassPermissions`; no doc under docs/ or README.md describes the old grant (only the frozen CHUPA_PLAN.md does).",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
