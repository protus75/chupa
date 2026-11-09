---
id: declined-box-000109-15f9eadf
kind: declined
link: box-000109-15f9eadf
reopen_after_days: 90
---
Before creating a ticket worktree, `prepare_worktree` in `chupa/stages.py` runs `git worktree remove --force` whenever the target path exists. The note warns that if the path is a leftover directory git does not know as a worktree, the removal fails with a GitError and every rerun of that stem fails. It proposes falling back to prune plus a delete through the filesystem seam, and adding a test.

The code matches the note: `prepare_worktree` (stages.py:469-470) calls `worktree_remove` whenever `path.exists()`, and `reconcile` (reconcile.py:55-56) and the base-worktree setup sites do the same. But nothing shows this path is reached. The engine never creates the worktree directory itself. It creates only the parent (`path.parent.mkdir`), and `git worktree add` creates the path and registers it, removing partial output when it fails or is interrupted by a catchable signal. The only remaining case is a SIGKILL inside git's own add window or someone deleting files by hand, and no run, journal or failure report shows a stem stuck this way. It is speculative hardening with no observed incident, so it falls below the admission bar. If it ever happened, the operator could clear it once by removing the directory.

- chupa/stages.py:466-481 prepare_worktree removes the worktree when path.exists(), otherwise prunes; it creates only path.parent before worktree_add
- chupa/git.py:95-98 worktree_remove runs `worktree remove --force` then prune and raises on failure
- chupa/reconcile.py:55-56 same exists-then-remove pattern
- Message origin is bootstrap-ingest with no stage, outcome or failure report; no open or merged ticket or registry record covers it

Message: box-000109-15f9eadf
