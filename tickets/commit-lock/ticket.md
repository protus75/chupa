---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/lockfile.py
- chupa/git.py
- chupa/tickets.py::intake
- chupa/merge.py::write_squash
- chupa/seams.py

## On-demand
- chupa/__main__.py
- chupa/doctor.py
- chupa/stages.py
- chupa/daemon.py
- chupa/runner.py
- chupa/author.py
- chupa/serve.py
- chupa/retro.py
- docs/how-chupa-works.md
- chupa/docs/host-contract.md
- tests/integration/test_lockfile.py
- tests/integration/test_git.py
- tests/integration/test_tickets.py

## Goal / Why
One lock, `.chupa/state/chupa.lock`, does two jobs: it keeps a second drain, serve or run from starting, and it keeps two processes from writing to `main` at once. A drain holds it for its whole run, often hours, but the git danger it guards against lasts seconds: a merge's squash commit landing while another process is between staging a ticket file and committing it. So any command that only needs to commit a ticket is refused for the whole drain. On 2026-11-10, `./dev.py review core-template-budget` was refused after the owner edited the ticket, and the operator had to wait for the drain to commit the edit before the review could run.

This ticket adds a second lock sized to that danger: a commit lock held only while git writes. It lives inside `chupa/git.py`, the one module every chupa git call already goes through, so no caller holds it and a new commit site cannot forget it. It is the base that `commit-lock-commands` builds on to move `review`, `confirm` and `reject` off the engine lock.

## Scope in / Scope out
- In: `chupa/lockfile.py` adds a `CommitLock` at `<state_dir>/commit.lock`. It is an advisory `flock` that records the same identity fields as `Lockfile`.
  - Acquire polls a non-blocking `flock` through injected clock and sleep seams. It gives up after `COMMIT_LOCK_WAIT_S = 60` seconds.
  - On timeout it raises `CommitLockTimeout`. That is its own exception type, not `LockHeld` or a subclass. Its message names the holder from the lockfile identity. Its paved road says to retry once that process finishes its commit, and never to delete the lockfile.
  - Release truncates the identity to empty before closing. A reader then sees an empty file once the lock is free, even while the releasing process lives on.
  - Within one process, a second asyncio task that wants the lock waits, as another process would. A task that asks again for the lock it already holds gets a `RuntimeError` at once, not a 60-second wait.
- In: `chupa/git.py`: `Git.__init__` takes a required `commit_lock` (a `CommitLock`) with no default. The methods that write the index or commit hold it for their whole run:
  - `commit(dir, message, *, only=())` returns the new `HEAD` sha. When `only` is given, it stages those paths first. If those paths then match `HEAD`, it makes no commit and returns `None`.
  - `merge_squash(dir, branch, message)` runs `merge --squash` and the commit, and returns the new sha.
  - `add` and `restore` hold the lock for their one call.
  - Read methods, `rebase`, and the branch and worktree methods do not take the lock.
- In: every caller of those methods drops its own `add` before `commit`. It uses the returned sha instead of a separate `rev_parse(..., "HEAD")`. The callers are in `chupa/tickets.py`, `chupa/merge.py`, `chupa/stages.py`, `chupa/daemon.py`, `chupa/runner.py`, `chupa/author.py`, `chupa/serve.py` and `chupa/retro.py`.
- In: `tickets.intake` journals `ticket_intake` only when `commit` returns a sha. If another process commits the same pending ticket first, intake skips it quietly instead of raising.
- In: the composition roots build one `CommitLock` per process from the configured `state_dir`, clock and sleep, and pass it to `Git`. The roots are `chupa/__main__.py` and `chupa/doctor.py`; doctor may build its `Git` after the config load. The CLI's top-level error handler maps `CommitLockTimeout` to exit 2 with its message and road, as it does `LockHeld`.
- In: update every test, harness or fake that builds a `Git`, or fakes `commit`, `merge_squash` or `add`, to the new constructor and return values. Use one shared test helper for the lock where that keeps each edit to one line.
- In: documentation:
  - `docs/how-chupa-works.md`: add a `commit.lock` row next to `chupa.lock` in the state-files table. The `chupa.lock` row says it is the engine lock, held by `run`, `drain`, `serve` and the verbs that still take it.
  - `chupa/docs/host-contract.md`: add one sentence to the lockfile paragraph saying git writes take `commit.lock` with a 60-second wait. The paragraph keeps `never delete the lockfile`.
- Out:
  - Which verbs take `chupa.lock`. `review`, `confirm` and `reject` change in `commit-lock-commands`.
  - The snapshot and the extension.
  - `doctor`'s lock probe.
  - The operator's own git commits, which cannot take the lock.

## Scope fence
- chupa/lockfile.py
- chupa/git.py
- chupa/__main__.py
- chupa/doctor.py
- chupa/tickets.py
- chupa/merge.py
- chupa/stages.py
- chupa/daemon.py
- chupa/runner.py
- chupa/author.py
- chupa/serve.py
- chupa/retro.py
- chupa/mergequeue.py
- docs/how-chupa-works.md
- chupa/docs/host-contract.md
- tests/unit/test_commit_lock.py
- tests/unit/test_hostfiles.py
- tests/unit/test_retro_measurements.py
- tests/harness/daemon_soak.py
- tests/harness/host_loop.py
- tests/harness/reliability_battery.py
- tests/harness/shakeout/bench.py
- tests/harness/shakeout/run.py
- tests/regress_status_optional_locks.py
- tests/integration/test_author.py
- tests/integration/test_box.py
- tests/integration/test_checkpoint.py
- tests/integration/test_cli.py
- tests/integration/test_covmap.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_daemon_soak.py
- tests/integration/test_daemon_soak_runner.py
- tests/integration/test_doctor.py
- tests/integration/test_drain.py
- tests/integration/test_fixture_host.py
- tests/integration/test_gates.py
- tests/integration/test_git.py
- tests/integration/test_heartbeat.py
- tests/integration/test_hostfiles.py
- tests/integration/test_inbox.py
- tests/integration/test_lint_verb.py
- tests/integration/test_lockfile.py
- tests/integration/test_merge.py
- tests/integration/test_mergequeue.py
- tests/integration/test_reconcile.py
- tests/integration/test_reject_queue.py
- tests/integration/test_scheduler.py
- tests/integration/test_stages.py
- tests/integration/test_status.py
- tests/integration/test_tickets.py

## Acceptance criteria
1. New `tests/unit/test_commit_lock.py` uses a fake clock and sleep. It keeps the `test-gate.toml` unit floors for `chupa/lockfile.py` and `chupa/git.py`, and covers these cases:
   - While another descriptor holds `commit.lock`, acquire waits, then succeeds once that descriptor releases before 60 seconds. It does not refuse on first contention.
   - When the holder never releases, acquire raises `CommitLockTimeout` at 60 seconds, naming the holder's pid. It neither waits forever nor acquires. `CommitLockTimeout` is not an instance of `LockHeld`.
   - After release, `commit.lock` is empty, not the stale identity.
   - A second task in the same process waits for the first task's release. The holding task asking again raises `RuntimeError` at once.
   - With a fake exec, `Git.commit(..., only=paths)` runs `add` and `commit` inside one hold and returns the sha. It returns `None` and runs no `commit` when the staged paths match `HEAD`. `Git.merge_squash` runs both git steps inside one hold.
2. `tests/integration/test_git.py`: with a real repository, a real `Git.commit` does not commit while another descriptor holds `commit.lock`, and it commits after release.
3. `tests/integration/test_tickets.py`: another `Git` commits a pending ticket between intake's status read and its commit. Intake raises nothing and journals no second `ticket_intake` for that stem.
4. `./dev.py test` exits 0.
5. `docs/how-chupa-works.md` has a `commit.lock` row in its state-files table.

## Verification
```
./dev.py test
```

## Definition of rejected
- A caller outside `chupa/git.py` and the composition roots takes, releases or holds the commit lock.
- The wait has no limit, or the limit is not 60 seconds.
- `Git` keeps an optional or default `commit_lock`, or a second, unlocked write path.
- Any code deletes or steals a lockfile.
- Which verbs take `chupa.lock` changes.

## Time budget
- expected: 90m
- stuck: 180m
