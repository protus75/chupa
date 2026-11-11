---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/git.py::Git.add
- chupa/git.py::Git.commit
- chupa/git.py::Git.merge_squash
- chupa/git.py::GitError
- chupa/tickets.py::intake
- chupa/merge.py::write_squash
- chupa/daemon.py::apply_rework

## On-demand
- chupa/stages.py
- chupa/runner.py
- chupa/author.py
- chupa/serve.py
- chupa/retro.py
- tests/integration/test_git.py
- tests/integration/test_tickets.py
- tests/integration/test_ladder.py
- tests/integration/test_serve_admission.py
- tests/integration/test_mergequeue.py
- tests/integration/test_daemon_composition.py

## Goal / Why
Every place chupa commits to `main` does the same three steps: `git.add(paths)`, `git.commit(..., only=paths)`, then `git.rev_parse(..., "HEAD")` to learn the new commit. `write_squash` does `merge_squash`, then `commit`, then `rev_parse`. Ticket `commit-lock` needs each of these to be one `Git` call, so a lock can be held around the whole write inside `chupa/git.py` with no caller involved. `commit-lock` tried to do this refactor and the lock in one ticket, about 55 files. On 2026-11-11 its Implement attempt gave up after two minutes, and Diagnose said to split it. This ticket is the first half: the `Git` API change with no lock. `commit-lock` then adds the lock on top.

When this ticket is done:
- `Git.commit` stages its own paths and returns the new commit's sha.
- `Git.merge_squash` commits and returns the sha.
- Callers no longer `add` before `commit` or `rev_parse` after it.

## Scope in / Scope out
- In: `chupa/git.py`:
  - `commit(dir, message, *, only=())` returns the new `HEAD` sha.
  - When `only` is given, it first stages those paths with `git update-index --add --remove -- <paths>`, not `git add`. A path that is gone from both the index and the worktree then records its deletion, where `git add` fails with `pathspec did not match any files`.
  - If the staged `only` paths then match `HEAD`, it makes no commit and raises `NothingToCommit`, a new `GitError` subclass in `chupa/git.py`. Every caller except `tickets.intake` lets it propagate, so each fails as a no-change `commit --only` fails today.
  - Without `only`, `commit` stages nothing and behaves as today (a commit with nothing staged still raises `GitError`).
  - `merge_squash(dir, branch, message)` runs `merge --squash` and then the commit, and returns the new sha.
- In: every caller of `commit` and `merge_squash` drops its own `add` before `commit`, and uses the returned sha instead of a separate `rev_parse(..., "HEAD")` or `rev_parse(..., MAIN)`. The callers are:
  - `chupa/tickets.py::intake`
  - `chupa/merge.py::write_squash`
  - `chupa/stages.py` (the records commit and `check_autofix`)
  - `chupa/daemon.py::apply_rework`
  - `chupa/runner.py` (`verdict_locked`, `reject_ticket`)
  - `chupa/author.py` (both commits)
  - `chupa/serve.py`
  - `chupa/retro.py`
- In: one exception in `chupa/daemon.py::apply_rework`: `restore_publication` keeps its `add` of written successors.
  - That `add` serves the `restore` that follows it, which can then remove untracked successor files. It does not stage for the undo commit.
  - `publish` in the same function drops its `add`.
  - The undo commit passes `only=` paths that `restore` has already removed from the index and worktree. The `update-index` staging above lets that commit record their deletion.
- In: `tickets.intake` catches `NothingToCommit` for a stem and journals no `ticket_intake` for it. If another process committed the same pending ticket first, intake skips it quietly instead of raising.
- In: tests that fake or wrap these methods follow the new signatures and return values:
  - The `merge_squash` fakes in `tests/integration/test_mergequeue.py` and `tests/integration/test_daemon_composition.py`.
  - The `add` and `commit` failure fakes in `tests/integration/test_daemon_composition.py` and `tests/integration/test_stages.py`.
  - The `Git.add`/`Git.commit` wrappers in `tests/integration/test_author.py`, `tests/integration/test_drain.py` and `tests/integration/test_ladder.py`.
  - The `rev_parse` mismatch fakes in `tests/integration/test_merge.py`, `tests/integration/test_mergequeue.py`, `tests/integration/test_serve_admission.py` and `tests/integration/test_daemon_composition.py`. These now inject the mismatch through the sha that `commit` or `merge_squash` returns, wherever the caller no longer calls `rev_parse`.
  - The tree-mismatch case in `tests/integration/test_serve_admission.py` wraps the three-argument `merge_squash`. It stages its defect file before delegating, so the defect still lands in the squash commit.
  - A test whose `add` failure no longer happens (because a caller dropped its `add`) moves its failure into `commit`.
- Out:
  - Any lock. `commit-lock` adds it.
  - `Git` construction, `chupa/lockfile.py`, `chupa/doctor.py`, `chupa/__main__.py`'s error handling.
  - `hosts/fixture/bin/claude` and `eval/`, which keep calling `add` then `commit`. `commit(only=)` on already-staged paths still commits them.
  - `rebase`, worktree and branch methods, and `chupa/mergequeue.py`'s `checkout --ours`.

## Scope fence
- chupa/git.py
- chupa/tickets.py
- chupa/merge.py
- chupa/stages.py
- chupa/daemon.py
- chupa/runner.py
- chupa/author.py
- chupa/serve.py
- chupa/retro.py
- tests/unit/test_git_commit.py
- tests/integration/test_git.py
- tests/integration/test_tickets.py
- tests/integration/test_merge.py
- tests/integration/test_mergequeue.py
- tests/integration/test_serve_admission.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_stages.py
- tests/integration/test_author.py
- tests/integration/test_drain.py
- tests/integration/test_ladder.py

## Acceptance criteria
1. New `tests/unit/test_git_commit.py` drives `Git` with a fake exec that records argv and returns scripted output, and never touches disk. It stubs `tickets.intake`'s ticket read, validation and journal through `monkeypatch`. It keeps the `test-gate.toml` unit floors for `chupa/git.py` (27) and `chupa/tickets.py` (11). Cases:
   - `commit(dir, msg, only=["a"])` runs `update-index --add --remove -- a` before `commit`, and returns the sha the fake reports for `HEAD`.
   - When the fake reports that the staged `only` paths match `HEAD`, `commit` raises `NothingToCommit`, runs no `commit`, and `NothingToCommit` is an instance of `GitError`.
   - `commit(dir, msg)` with no `only` runs no `update-index`.
   - `merge_squash(dir, "b", msg)` runs `merge --squash` then `commit`, and returns the sha.
   - `tickets.intake` with a fake `Git` whose `commit` raises `NothingToCommit` journals no `ticket_intake` and raises nothing.
2. `tests/integration/test_git.py`, with a real repository:
   - A file committed after `base`, then removed from the index and worktree by `Git.restore(..., source=base)`, is committed as a deletion by `Git.commit(..., only=[path])`. The call returns the new `HEAD` sha and does not raise `pathspec did not match`.
   - `Git.commit(..., only=[path])` on a path that matches `HEAD` raises `NothingToCommit` and leaves `HEAD` unchanged.
   - `Git.merge_squash` returns the sha that `git rev-parse HEAD` then prints.
3. `tests/integration/test_tickets.py`: another `Git` commits a pending ticket between intake's status read and its commit. Intake raises nothing and journals no second `ticket_intake` for that stem.
4. The split cases in `tests/integration/test_ladder.py` that assert `git status --porcelain == ""` after a refused rework still pass unchanged.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A caller of `commit` or `merge_squash` in `chupa/` still runs `add` before it (other than `restore_publication`) or `rev_parse` after it to learn the new commit.
- `Git.commit` returns `None` for any case.
- Any lock is added, or `Git`'s constructor changes.

## Time budget
- expected: 60m
- stuck: 120m
