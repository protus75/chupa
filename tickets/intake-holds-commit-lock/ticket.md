---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/tickets.py::intake
- chupa/git.py::Git
- chupa/lockfile.py::CommitLock
- docs/how-chupa-works.md#3.2 Intake
- tests/integration/test_git.py::commit_lock

## On-demand
- tests/integration/test_tickets.py

## Goal / Why
`intake` is safe today only because its caller holds the engine lock (`chupa.lock`); its docstring says so. Its `git status` read and its stray check ("staged changes outside pending ticket files") run with no lock. Only each per-stem commit takes the commit lock (`commit.lock`), inside `Git.commit`.

`commit-lock` moved every git write in the engine onto the commit lock, but left intake's precondition on the engine lock. On 2026-11-11 the drain's requisition review parked `commit-lock-commands` (premise_failed, `unguarded-seam`) because that ticket runs intake from `review`, `confirm` and `reject` while a drain holds the engine lock. A drain's `Git.merge_squash` stages a squash in the shared index and then commits it under the commit lock. An intake that reads status between those two steps sees staged non-ticket paths and raises `IntakeRefused` for no real reason.

After this change, intake's status read, evidence listing, stray check, frontmatter stamping and per-stem commits all run inside one commit-lock hold. A caller no longer needs the engine lock for intake's git safety. Every future caller that runs intake without the engine lock gets this for free.

## Scope in / Scope out
- In: `chupa/tickets.py::intake`:
  - Wraps its whole body, from the `git.status_porcelain` read through the last commit, in one `async with git._commit_lock:` hold.
  - Commits each stem with `git._commit(...)` inside that hold, never `git.commit(...)`, because `CommitLock` raises `RuntimeError` on a nested hold by the same task. `intake` already calls `git._run`, so this adds no new kind of access and no new `Git` method.
  - The `except NothingToCommit` skip stays, because a commit made outside chupa (a human `git commit`) bypasses the commit lock.
  - Its docstring replaces "The caller holds the single-writer lock." with a sentence saying that intake holds the commit lock across its status read, stray check and commits, so its git work needs no engine lock.
  - A `CommitLockTimeout` propagates to the caller unchanged.
- In: `tests/unit/test_git_commit.py::test_intake_skips_concurrent_commit`: its `FakeGit` gains a `_commit_lock` that counts entries and tracks whether it is held, and its `commit` method is renamed `_commit`. `status_porcelain` and `_commit` each assert the lock is held when called. This is the unit test that runs the new hold for the `chupa/tickets.py` coverage floor in `test-gate.toml`.
- In: `docs/how-chupa-works.md` section 3.2 Intake: add one bullet saying that intake reads status, checks for stray staged paths and commits under one `commit.lock` hold.
- Out:
  - No change to which verbs call intake, and no caller drops the engine lock (that is `commit-lock-commands`).
  - No change to `chupa/git.py`, `chupa/lockfile.py`, or `COMMIT_LOCK_WAIT_S`.
  - `test_intake_skips_ticket_committed_after_status` keeps passing unchanged; its second `Git` uses a different state directory, so it never contends for this lock.

## Scope fence
- chupa/tickets.py
- docs/how-chupa-works.md
- tests/integration/test_tickets.py
- tests/unit/test_git_commit.py

## Acceptance criteria
1. A new test in `tests/integration/test_tickets.py` covers the race:
   - It uses the `repo` fixture, writes a valid pending ticket, and stages a change to `chupa/thing.py`.
   - It takes a second `CommitLock` on the fixture `Git`'s state directory (`tmp_path / ".chupa/state"`) and starts `intake` as a task while holding it.
   - It yields until the task has polled the lock, unstages `chupa/thing.py` with `git reset -q -- chupa/thing.py`, then releases the lock.
   - Awaiting the task returns `committed == ("t-one",)` and `refused == {}`, not `IntakeRefused` naming `chupa/thing.py`, and `main` holds the ticket's commit.
2. All existing intake tests in `tests/integration/test_tickets.py` still pass, including `test_staged_change_outside_ticket_files_refuses_intake` (a stray that is still staged when intake gets the lock is refused) and `test_intake_skips_ticket_committed_after_status`.
3. `tests/unit/test_git_commit.py::test_intake_skips_concurrent_commit` asserts the fake lock was entered exactly once and was held during both the status read and the `_commit` call. It fails if intake reads status before taking the lock or calls the public `commit`.
4. `./dev.py test tests/unit/test_git_commit.py tests/integration/test_tickets.py tests/integration/test_git.py tests/unit/test_commit_lock.py` exits 0.
5. `chupa/tickets.py::intake`'s docstring no longer says the caller holds the single-writer lock, and `docs/how-chupa-works.md` section 3.2 names the `commit.lock` hold.

## Verification
```
./dev.py test tests/unit/test_git_commit.py tests/integration/test_tickets.py tests/integration/test_git.py tests/unit/test_commit_lock.py
```

## Definition of rejected
- `intake` reads `git status` or runs its stray check outside a commit-lock hold.
- `intake` calls `git.commit` inside its own hold, which raises `RuntimeError` on the nested hold.
- A second lock, or a new `Git` method, is added for this.
- Any intake caller is changed.

## Time budget
- expected: 30m
- stuck: 60m
