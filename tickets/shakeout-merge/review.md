# Review: approve

The conflicted_rebase member edits the same line on main after Review approves, then asserts all of these: the refusal is gate_failed at merge with a post_rebase_regate finding, main's HEAD does not move, the branch head equals the reviewed SHA, and no rebase-merge/rebase-apply state or 'rebase in progress' status shows at refusal or at worktree cleanup. GROUPS gains 'merge' after 'recovery', the test exercises the member through run_member, and every touched file is inside the fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "ed80ca5a0cfaf431bf597ee0c8569f4683488986",
  "stem": "shakeout-merge",
  "reviewed_sha": "ed80ca5a0cfaf431bf597ee0c8569f4683488986",
  "summary": "The conflicted_rebase member edits the same line on main after Review approves, then asserts all of these: the refusal is gate_failed at merge with a post_rebase_regate finding, main's HEAD does not move, the branch head equals the reviewed SHA, and no rebase-merge/rebase-apply state or 'rebase in progress' status shows at refusal or at worktree cleanup. GROUPS gains 'merge' after 'recovery', the test exercises the member through run_member, and every touched file is inside the fence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
