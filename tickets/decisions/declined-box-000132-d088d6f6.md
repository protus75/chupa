---
id: declined-box-000132-d088d6f6
kind: declined
link: box-000132-d088d6f6
reopen_after_days: 90
---
The suggestion is to make `worktree_root` a non-optional config field once config has loaded, so `chupa/runner.py` and `chupa/stages.py` no longer need `assert worktree_root is not None`. It describes no wrong runtime behavior; it is a typing and readability cleanup.

This is a refactor. Neither the message nor the open tickets show that a `None` `worktree_root` reaches a call site at runtime and causes a crash or wrong result. The asserts only narrow the type for the type checker. The open ticket `stages-base-worktree-helper` already merges the base-worktree setup sites in `chupa/stages.py`, including the missing assert in `check_hosts`, so the one drift worth fixing is already covered. The triage bar declines cleanup and refactor proposals that are not tied to incorrect runtime behavior.

- The message class is `suggestion` and its origin is `bootstrap-ingest`. It reports no stage, outcome, or failure.
- The proposal is to resolve the field to non-optional so call sites need no assert, which is a type-shape change only.
- The open ticket `stages-base-worktree-helper` already consolidates the `worktree_root` path setup in `chupa/stages.py` and notes that `check_hosts` lacks the assert.

Message: box-000132-d088d6f6
