---
id: declined-box-000098-2dcb343f
kind: declined
link: box-000098-2dcb343f
reopen_after_days: 90
---
A bootstrap review note warned that when the stage seam raises after `run` has journaled `to: running`, the stem is left in `running` with no terminal state, and `status` shows it as in flight until reconcile-on-entry exists. It asked for a test, once reconcile shipped, showing that the next invocation reaps such a crashed run.

The behavior gap is already closed. Reconcile-on-entry exists in `chupa/reconcile.py`. `orphans()` treats any stem whose last state transition is `running` with no later terminal as an orphan. `reconcile()` harvests it, journals `abandoned` with a recovery_alert, and removes its worktree. `run_ticket` in `chupa/runner.py` and the drain loop in `chupa/drain.py` both call it on entry, under the lock. So a crashed `run` is reaped on the next invocation. The only thing left from the note is a test that pins this. That is a test-only improvement with no reachable incorrect runtime behavior, so it falls under the decline rule.

- chupa/reconcile.py:17-38 `orphans` counts a stem with `to: running` and no later terminal transition as an orphan
- chupa/reconcile.py:41-59 `reconcile` journals `abandoned` plus a recovery_alert signal for each orphan and removes its worktree
- chupa/runner.py:485 `run_ticket` calls `reconcile(...)` right after acquiring the lock, before admitting the stem
- chupa/drain.py:258 drain also calls `reconcile(...)` on entry
- tests/integration/test_reconcile.py already exists and exercises `orphans`/`reconcile`
- Decision declined-box-000083-e58f5068 already records that reconcile-on-entry exists and that terminal transitions are now written

Message: box-000098-2dcb343f
