# Review: approve

When lint runs from a linked worktree, `_lint` now reads the main checkout's journal through `git_common_dir` and the repo-relative `state_dir`. The main checkout keeps its existing journal path. The diff adds the integration test and the carried reproducer the ticket asks for, both checking `1/1` with exit 0, and updates Workflow step 2 in `docs/host-authoring.md`. Nothing is written and no other verb's config handling changes.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "481b212aee8ec24135a070aae901974ca3f237de",
  "stem": "lint-worktree-journal",
  "reviewed_sha": "481b212aee8ec24135a070aae901974ca3f237de",
  "summary": "When lint runs from a linked worktree, `_lint` now reads the main checkout's journal through `git_common_dir` and the repo-relative `state_dir`. The main checkout keeps its existing journal path. The diff adds the integration test and the carried reproducer the ticket asks for, both checking `1/1` with exit 0, and updates Workflow step 2 in `docs/host-authoring.md`. Nothing is written and no other verb's config handling changes.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
