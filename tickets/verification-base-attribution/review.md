# Review: approve

The diff adds merge_base and worktree_add_detached with ref guards. gather_evidence now re-runs red commands once in a detached base worktree, cleans it up with remove + prune in a finally block, marks base_red, spools the base output and files one deduplicated failure_report. VerificationGate ignores base_red results, and merge regating gets the same attribution through gather_evidence. Every fenced test meets its acceptance criterion.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "ddc6d4087f1fa76c284a0d1336d8216cd511b0b6",
  "stem": "verification-base-attribution",
  "reviewed_sha": "ddc6d4087f1fa76c284a0d1336d8216cd511b0b6",
  "summary": "The diff adds merge_base and worktree_add_detached with ref guards. gather_evidence now re-runs red commands once in a detached base worktree, cleans it up with remove + prune in a finally block, marks base_red, spools the base output and files one deduplicated failure_report. VerificationGate ignores base_red results, and merge regating gets the same attribution through gather_evidence. Every fenced test meets its acceptance criterion.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
