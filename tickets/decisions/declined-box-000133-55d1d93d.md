---
id: declined-box-000133-55d1d93d
kind: declined
link: box-000133-55d1d93d
reopen_after_days: 90
---
`reconcile` in `chupa/reconcile.py` runs `worktree_prune` once more after its reap loop, but `Git.worktree_remove` already prunes after each removal. The suggestion is to prune once per reaped batch or drop one of the two prune calls. The only cost is a redundant git call.

This is cleanup, not a fix for a harmful bug. Running `git worktree prune` more than once is idempotent, so the extra call changes no outcome. The note itself says the outer prune only matters when no worktree existed, and then it is a harmless no-op. Nothing shows a wrong runtime result, a failure, or a cost anyone would notice, so there is nothing to measure after a change.

- The message says the prune after the loop is redundant because `Git.worktree_remove` already prunes. That is extra work, not wrong behavior.
- `git worktree prune` is idempotent, so pruning twice cannot change state or results.
- No failure report, stage, or outcome comes with it (stage=null, outcome=null, origin=bootstrap-ingest).
- No open ticket or registry record covers this exact item. Related reconcile records (declined-box-000131-2f325e7a) cover crash-point tests, not prune redundancy.

Message: box-000133-55d1d93d
