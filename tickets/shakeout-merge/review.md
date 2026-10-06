# Review: snag

The member's 'no rebase in progress' check can never fail: the production cleanup force-removes the worktree before the check runs, so a regression that left a rebase in progress would still pass green.

## Findings

- [logic] eval/shakeout/merge.py:66 The assertion `not (bench.repo / '.git' / 'worktrees' / stem / 'rebase-merge').exists()` runs after `bench.drain()`. By then `runner.py` has already called `git worktree remove --force` and `prune` on the failed ticket's worktree, which deletes `.git/worktrees/<stem>` whether or not a rebase was left in progress. The check is therefore always true. The `rebase-apply` backend is never checked, and the member never runs the `git status` observation the ticket names. If `Git.rebase` stopped aborting, the member would still pass, which the Definition of rejected forbids ('The member passes with a rebase left in progress'). The `reviewed_sha` check on line 64 does not cover this either: a rebase stopped mid-way never moves the branch ref. (do instead: Observe the worktree at the moment of refusal, before cleanup. In the member, wrap `bench.git.worktree_remove` (or the bench's Git seam) so that before delegating for this stem it runs `git status` in the worktree and records the state. Assert that neither `rebase-merge` nor `rebase-apply` exists under `git rev-parse --git-dir`, that the worktree HEAD equals `review.reviewed_sha`, and that main's HEAD at that moment equals `main_at_admission[0]`. Then assert on the recorded state after `drain()`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "dee84e4c8a206059d11c5b1c7512123031d7a86f",
  "stem": "shakeout-merge",
  "reviewed_sha": "dee84e4c8a206059d11c5b1c7512123031d7a86f",
  "summary": "The member's 'no rebase in progress' check can never fail: the production cleanup force-removes the worktree before the check runs, so a regression that left a rebase in progress would still pass green.",
  "findings": [
    {
      "code": "logic",
      "path": "eval/shakeout/merge.py",
      "line": 66,
      "message": "The assertion `not (bench.repo / '.git' / 'worktrees' / stem / 'rebase-merge').exists()` runs after `bench.drain()`. By then `runner.py` has already called `git worktree remove --force` and `prune` on the failed ticket's worktree, which deletes `.git/worktrees/<stem>` whether or not a rebase was left in progress. The check is therefore always true. The `rebase-apply` backend is never checked, and the member never runs the `git status` observation the ticket names. If `Git.rebase` stopped aborting, the member would still pass, which the Definition of rejected forbids ('The member passes with a rebase left in progress'). The `reviewed_sha` check on line 64 does not cover this either: a rebase stopped mid-way never moves the branch ref.",
      "paved_road": "Observe the worktree at the moment of refusal, before cleanup. In the member, wrap `bench.git.worktree_remove` (or the bench's Git seam) so that before delegating for this stem it runs `git status` in the worktree and records the state. Assert that neither `rebase-merge` nor `rebase-apply` exists under `git rev-parse --git-dir`, that the worktree HEAD equals `review.reviewed_sha`, and that main's HEAD at that moment equals `main_at_admission[0]`. Then assert on the recorded state after `drain()`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
