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
- tests/integration/test_ladder.py

## Goal / Why
One lock, `.chupa/state/chupa.lock`, does two jobs: it keeps a second drain, serve or run from starting, and it keeps two processes from writing to `main` at once. A drain holds it for its whole run, often hours, but the git danger it guards against lasts seconds: a merge's squash commit landing while another process is between staging a ticket file and committing it. So any command that only needs to commit a ticket is refused for the whole drain. On 2026-11-10, `./dev.py review core-template-budget` was refused after the owner edited the ticket, and the operator had to wait for the drain to commit the edit before the review could run.

This ticket adds a second lock sized to that danger: a commit lock held only while git writes. It lives inside `chupa/git.py`, the one module every chupa git call already goes through, so no caller holds it and a new commit site cannot forget it. It is the base that `commit-lock-commands` builds on to move `review`, `confirm` and `reject` off the engine lock.

## Scope in / Scope out
- In: `chupa/lockfile.py` adds a `CommitLock` at `<state_dir>/commit.lock`. It is an advisory `flock` whose identity records `pid`, `host`, `state_dir` and `started_at` (the acquire time) and no `instance_id`, so building it needs no `Git`.
  - Construction does no I/O. Only acquire creates the state directory and `commit.lock`. `chupa/__main__.py` builds the lock for every verb, including read-only `snapshot`, `watch`, `status`, `lint` and `doctor` and idle `kill`, `pause` and `resume`; `tests/integration/test_watch.py`, `tests/integration/test_kill_cli_activation.py` and `tests/integration/test_control_cli.py` require those verbs to leave the state directory unchanged.
  - Acquire polls a non-blocking `flock` through injected clock and sleep seams. It gives up after `COMMIT_LOCK_WAIT_S = 60` seconds.
  - On timeout it raises `CommitLockTimeout`. That is its own exception type, not `LockHeld` or a subclass. Its message names the holder from the lockfile identity. Its paved road says to retry once that process finishes its commit, and never to delete the lockfile.
  - Release truncates the identity to empty before closing. A reader then sees an empty file once the lock is free, even while the releasing process lives on.
  - Within one process, a second asyncio task that wants the lock waits, as another process would. A task that asks again for the lock it already holds gets a `RuntimeError` at once, not a 60-second wait.
- In: `chupa/git.py`: `Git.__init__` takes a required `commit_lock` (a `CommitLock`) with no default. The methods that write the index or commit hold it for their whole run:
  - `commit(dir, message, *, only=())` returns the new `HEAD` sha. When `only` is given, it stages those paths first with `git update-index --add --remove -- <paths>`, not `git add`. A path that is gone from both the index and the worktree then records its deletion; `git add` fails on it with `pathspec did not match any files`. If those paths then match `HEAD`, it makes no commit and raises `NothingToCommit`, a `GitError` subclass defined in `chupa/git.py`. Every caller except `tickets.intake` lets it propagate, so each fails as a no-change `commit --only` fails today.
  - `merge_squash(dir, branch, message)` runs `merge --squash` and the commit, and returns the new sha.
  - `add` and `restore` hold the lock for their one call.
  - Read methods, `rebase`, `rebase_continue`, and the branch and worktree methods do not take the lock. The merge queue's conflict resolution in `chupa/mergequeue.py` (a raw `checkout --ours` in a ticket worktree) also stays unlocked. It runs only in ticket worktrees and never on the main checkout.
- In: every caller of those methods drops its own `add` before `commit`. It uses the returned sha instead of a separate `rev_parse(..., "HEAD")`. The callers are in `chupa/tickets.py`, `chupa/merge.py`, `chupa/stages.py`, `chupa/daemon.py`, `chupa/runner.py`, `chupa/author.py`, `chupa/serve.py` and `chupa/retro.py`.
  - One exception: in `chupa/daemon.py`, `apply_rework`'s `restore_publication` keeps its `add` of written successors. That add serves the `restore` that follows it, which can then remove untracked successor files; it does not stage for the undo commit. `publish` in the same function drops its `add`.
  - The undo commit in `restore_publication` passes `only=` paths that `restore` has already removed from the index and worktree. The `update-index` staging above is what lets that commit record their deletion.
- In: `tickets.intake` catches `NothingToCommit` and journals no `ticket_intake` for that stem. If another process commits the same pending ticket first, intake skips it quietly instead of raising.
- In: the composition roots build one `CommitLock` per process from the configured `state_dir`, clock and sleep, and pass it to `Git`. The roots are:
  - `chupa/__main__.py`.
  - `eval/harness.py` (both `Git` constructions) and `eval/diagnose.py`.
  - `hosts/fixture/bin/claude`, which builds its `CommitLock` under the fixture host's `.chupa/state` and calls `commit(..., only=edits)` instead of `add` followed by `commit`.
  - `chupa/doctor.py`: `check()` gains a required `sleep` parameter. Its `git` row moves after the config load and builds `Git` from the loaded `state_dir`, so the rows run in the order venv, config, git, lock, journal, core (was venv, git, config, ...). When the config fails to load, the `git` row fails with the detail `not checked: config did not load; fix the config and rerun doctor`. The hard-coded row orders in `tests/integration/test_doctor.py` change to match.
- In: the CLI's top-level error handler maps `CommitLockTimeout` to exit 2 with its message and road, as it does `LockHeld`.
- In: update every test, harness or fake that builds a `Git`, or fakes `commit`, `merge_squash` or `add`, to the new constructor and return values. Integration tests and harnesses build their `CommitLock` through one shared helper defined in `tests/integration/test_git.py`, which they import as they already import from `tests/integration/test_cli.py`. Unit tests use their own in-memory fakes and never import it. The tree-mismatch case in `tests/integration/test_serve_admission.py` wraps the three-argument `merge_squash` and stages its defect file before delegating, so the defect still lands in the squash commit.
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
- eval/harness.py
- eval/diagnose.py
- hosts/fixture/bin/claude
- tests/integration/test_serve_admission.py
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
- tests/integration/test_ladder.py

## Acceptance criteria
1. New `tests/unit/test_commit_lock.py` uses a fake clock and sleep and never touches disk. It replaces `chupa.lockfile`'s `os` and `fcntl` names with an in-memory fake that can simulate another holder, and stubs `tickets.intake`'s ticket read, validation and journal through `monkeypatch`. It keeps the `test-gate.toml` unit floors for `chupa/lockfile.py` and `chupa/git.py`, and covers these cases:
   - While the fake's other holder has `commit.lock`, acquire waits, then succeeds once that holder releases before 60 seconds. It does not refuse on first contention.
   - When the holder never releases, acquire raises `CommitLockTimeout` at 60 seconds, naming the holder's pid. It neither waits forever nor acquires. `CommitLockTimeout` is not an instance of `LockHeld`.
   - Constructing a `CommitLock` makes no call on the fake `os` or `fcntl`.
   - A second task in the same process waits for the first task's release. The holding task asking again raises `RuntimeError` at once.
   - With a fake exec, `Git.commit(..., only=paths)` runs `update-index --add --remove` and `commit` inside one hold and returns the sha. It raises `NothingToCommit` and runs no `commit` when the staged paths match `HEAD`. `Git.merge_squash` runs both git steps inside one hold. `Git.add` and `Git.restore` each run their one git call inside a hold, not outside it.
   - With a fake `Git` whose `commit` raises `NothingToCommit`, `tickets.intake` journals no `ticket_intake` and raises nothing (this keeps the `chupa/tickets.py` floor).
   - The CLI's top-level handler turns a `CommitLockTimeout` raised by a verb into exit 2 with the message on stderr, not a traceback (this keeps the `chupa/__main__.py` floor).
2. `tests/integration/test_lockfile.py`: with real files, a `CommitLock` acquire waits while another descriptor holds `commit.lock` and succeeds after it releases. After release `commit.lock` is empty, not the stale identity. Before the first acquire, a constructed `CommitLock` has not created `commit.lock` or its state directory.
3. `tests/integration/test_git.py`, with a real repository:
   - A real `Git.commit` does not commit while another descriptor holds `commit.lock`, and it commits after release.
   - A file committed after `base` and then removed from the index and worktree by `Git.restore(..., source=base)` is committed as a deletion by `Git.commit(..., only=[path])`. The call returns a sha and does not raise `pathspec did not match`.
4. `tests/integration/test_tickets.py`: another `Git` commits a pending ticket between intake's status read and its commit. Intake raises nothing and journals no second `ticket_intake` for that stem.
5. `tests/integration/test_doctor.py`: with a config that fails to load, the rows are named venv, config, git, lock, journal, core in that order, and the `git` row fails with the detail `not checked: config did not load; fix the config and rerun doctor`, not a git probe result.
6. `./dev.py test` exits 0, including the unchanged split cases in `tests/integration/test_ladder.py` that assert `git status --porcelain == ""` after a refused rework.
7. `docs/how-chupa-works.md` has a `commit.lock` row in its state-files table.

## Verification
```
./dev.py test
```

## Definition of rejected
- Code under `chupa/`, `eval/` or `hosts/` outside `chupa/git.py` and the composition roots takes, releases or holds the commit lock. Tests may acquire it directly.
- The wait has no limit, or the limit is not 60 seconds.
- `Git` keeps an optional or default `commit_lock`.
- A write to the main checkout's index or a commit on it runs without holding the commit lock.
- Any code deletes or steals a lockfile.
- Which verbs take `chupa.lock` changes.

## Time budget
- expected: 90m
- stuck: 180m
