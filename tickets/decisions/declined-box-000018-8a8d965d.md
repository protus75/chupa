---
id: declined-box-000018-8a8d965d
kind: declined
link: box-000018-8a8d965d
reopen_after_days: 90
---
A bootstrap note says the lockfile test that checks the lock file descriptor is not inherited by child processes does so by reading a private attribute with `os.get_inheritable`. It proposes a behavioral test instead: acquire the lock, spawn a child that keeps its inherited descriptors, release the lock in the parent, and show that a third process can acquire it while the child is still running.

This only improves a test. The message shows no runtime fault: by its own account, the existing assertion checks that the descriptor is non-inheritable, so the lock does not leak to children today. No incident shows a child process holding the engine lock after the parent released it. Under the triage bar, a test-only improvement is a decision unless it is tied to reachable incorrect runtime behavior. The suggestion does not duplicate an open ticket, a merged ticket, or a decision. decision-box-000017-e78ba696 also covers `chupa/lockfile.py`, but it is about instance_id and the FileSystem seam, not about whether children inherit the descriptor.

- The message class is suggestion and its origin is bootstrap-ingest, with no stage, outcome, or failure report.
- The message says the existing test already asserts that the descriptor is non-inheritable, so the guarded behavior is pinned, just through a private attribute.
- No open ticket or merged stem covers lockfile descriptor inheritance. decision-box-000017-e78ba696 covers other lockfile concerns (instance_id, the FileSystem seam).
- Reopen if a refactor of lockfile.py leaves the private-attribute test passing while a child process keeps the lock, or if an incident shows a spawned child (provider CLI, git, or test runner) holding the engine lock after the parent released it.

Message: box-000018-8a8d965d
