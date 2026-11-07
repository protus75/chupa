---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
none

## Context
- chupa/git.py
- chupa/seams.py
- chupa/serve.py
- chupa/stages.py
- chupa/merge.py
- chupa/observe.py
- tests/test_git.py
- tests/regress_graph_lanes.py

## Goal / Why
Killing a running `git status` leaves a stale `.git/index.lock`. After that, every git write in that checkout (`add`, `commit`, `merge`) fails with `Unable to create '.../index.lock': File exists` until someone deletes the lock by hand.

Chupa kills `git status` as normal behavior:
- serve's `scan` runs `intake`, which calls `Git.status_porcelain` on the main checkout every `SERVE_POLL_S`, under `Serve.mutations`;
- `Serve.abort` (a kill or stop) cancels that task;
- cancelling `SubprocessExec.run` SIGKILLs the child's process group (`chupa/seams.py`, the `except BaseException` path that calls `_kill_and_wait`).

`git status` takes `index.lock` while it refreshes the stat cache, and SIGKILL skips git's lockfile cleanup. So a `./dev.py kill` or `stop` that lands inside that window wedges the checkout for the next writer.

Observed 2026-11-07: all three `tests/test_host_loop.py` tests errored at setup when the fixture stopped serve and triage's `git add` hit the stale lock (`evidence/host-loop-index-lock.txt`). Reproduced with `evidence/stale_lock.py` on git 2.43.0: SIGKILL during `git status` left `index.lock` in 5 of 5 trials, while `git --no-optional-locks status` never took the lock in 5 of 5 (`evidence/stale-lock-repro.txt`).

After this change every `git status` chupa runs passes the `--no-optional-locks` global option, so killing it cannot leave a lock behind.

## Scope in / Scope out
- In: `chupa/git.py`: `Git.status_porcelain(dir, *args)` runs `self._run(dir, "--no-optional-locks", "status", "--porcelain", *args)`, so its argv is `["git", "-C", <dir>, "--no-optional-locks", "status", "--porcelain", *args]`. It is the only place in `chupa/` that builds a `status` argv.
- In: callers that build their own `status` argv switch to `status_porcelain` and pass the same extra arguments:
  - `chupa/stages.py` `dirty_code`: `"--untracked-files=all", "-z"`;
  - `chupa/merge.py` `dirty_overlap`: `"-z"`;
  - `chupa/observe.py` `uncommitted_tickets`: `"--", "tickets"`, through the existing `ctx.git` and `asyncio.run` pattern of `git_output`.
- In: `tests/test_git.py`: `test_every_call_is_dir_pinned_and_passes_env_and_timeout` pins the new argv, and new `test_status_porcelain_takes_no_optional_locks` asserts that `status_porcelain(REPO, "-z")` produces argv `["git", "-C", "/repo", "--no-optional-locks", "status", "--porcelain", "-z"]`.
- In: new `tests/regress_status_optional_locks.py`, the carried reproducer. Like `tests/regress_graph_lanes.py`, it puts the repo root on `sys.path` and imports `chupa.git.Git`. It builds a `Git` with a recording fake exec whose `run` returns `(0, "", "")`, and calls `status_porcelain` on a path.
  - Recorded argv contains `--no-optional-locks` before `status`: prints `{"regression_result": "pass"}` and exits 0.
  - Recorded argv contains `status` without it: prints `{"regression_result": "defect"}` and exits 1.
  - Anything else (import failure, no call recorded): the traceback goes to stderr, and it prints `{"regression_result": "error"}` and exits 2.
- Out:
  - `Git._call` and every non-status git verb;
  - `Git.describe` (`describe --dirty` also refreshes the index, but runs only at startup and is not killed by `abort`);
  - the kill and cancel behavior of `SubprocessExec`;
  - `eval/host_loop.py`, and test helpers that run `git status` directly.

## Scope fence
- chupa/git.py
- chupa/stages.py
- chupa/merge.py
- chupa/observe.py
- tests/test_git.py
- tests/regress_status_optional_locks.py

## Acceptance criteria
1. `./dev.py test tests/test_git.py` exits 0. It includes `test_status_porcelain_takes_no_optional_locks`, which fails if the flag is missing, follows `status`, or the extra arguments are dropped or reordered.
2. `grep -rn '"status"' chupa/git.py chupa/stages.py chupa/merge.py chupa/observe.py` shows `"status"` as a git argument only in `Git.status_porcelain`. Other occurrences of the string are not git argv.
3. `uv run python tests/regress_status_optional_locks.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_git.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a git verb other than `status` gains `--no-optional-locks`, or `Git._call` changes;
- a code path deletes, or tolerates, an existing `index.lock`;
- the kill or cancel behavior in `chupa/seams.py` changes;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 20m
- stuck: 60m

## Regression
```
uv run python tests/regress_status_optional_locks.py
```
- carries: tests/regress_status_optional_locks.py
