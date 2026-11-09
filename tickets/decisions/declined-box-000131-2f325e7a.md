---
id: declined-box-000131-2f325e7a
kind: declined
link: box-000131-2f325e7a
reopen_after_days: 90
---
The suggestion asks for a test of one crash point in `reconcile` (`chupa/reconcile.py`). An orphaned run is journaled `abandoned` before its worktree is removed. The test would make `git.worktree_remove` raise after that write, then check that the next reconcile reaps nothing and dispatch still goes ahead.

This only asks for more test coverage. It reports no wrong behavior a user could hit. In current code the journal is written before the wipe on purpose (comment at line 54). Once `abandoned` is journaled, `orphans()` no longer counts the stem as running, so the next reconcile reaps nothing for it. The leftover worktree is removed when the next run of that stem tears down and recreates it. Like decisions 000098 and 000128, this is declined until there is a real failure.

- chupa/reconcile.py:52-53 writes the `abandoned` transition and the recovery alert before the worktree is removed
- chupa/reconcile.py:54 comment: 'Journal before wipe: a wipe that fails leaves a leftover the next run's teardown-and-create removes.'
- chupa/reconcile.py:55-56 calls `git.worktree_remove` with no try block, so a failure reaches the caller after the journal writes
- The message reports no observed failure, stuck stem or blocked dispatch

Message: box-000131-2f325e7a
