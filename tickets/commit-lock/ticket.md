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
- chupa/__main__.py::_review
- chupa/__main__.py::_verdict
- chupa/tickets.py::intake
- chupa/merge.py::write_squash
- chupa/observe.py::lock_holder
- chupa/observe.py::snapshot
- vscode-chupa/media/view.js

## On-demand
- chupa/runner.py
- chupa/drain.py
- chupa/serve.py
- chupa/daemon.py
- chupa/stages.py
- chupa/author.py
- chupa/retro.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- chupa/docs/host-contract.md
- tests/integration/test_lockfile.py
- tests/integration/test_review_command.py
- tests/integration/test_control_cli.py
- tests/integration/test_watch.py

## Goal / Why
One lock, `.chupa/state/chupa.lock`, does two jobs: it keeps a second drain, serve or run from starting, and it keeps two processes from writing to `main` at once. A drain holds it for its whole run, often hours, but the danger it guards against in git lasts a second or two: a merge's squash commit landing while another process is between staging a ticket file and committing it. So every command that only needs to commit a ticket is refused for the whole drain. On 2026-11-10, `./dev.py review core-template-budget` was refused after the owner edited the ticket, and the operator had to wait about 8 minutes for the drain to commit the edit itself before the review could run. The tickets view greys Review whenever any engine runs, even for committed tickets that never needed the lock, and greys Confirm and Reject on edited tickets for the same reason.

After this change there are two locks. The engine lock (`chupa.lock`) is held only by `run`, `drain` and `serve`, and they still refuse each other. The new commit lock (`.chupa/state/commit.lock`) is held only around each sequence of git writes to the main checkout, by the engine and by `review`, `confirm` and `reject`. A command that finds the commit lock held waits for it, up to 60 seconds, then refuses, naming the holder and saying what to do. `review` and `confirm`/`reject` work while a drain runs, and the tickets view stops greying them. The view header shows both locks.

## Scope in / Scope out
- In: `chupa/lockfile.py`: the commit lock at `<state_dir>/commit.lock`, an advisory `flock` like the engine lock and recording the same identity fields.
  - Acquire polls a non-blocking `flock` through the injected clock and sleep seams and gives up after `COMMIT_LOCK_WAIT_S = 60` seconds. On timeout it raises an error whose message names the holder from the lockfile identity. The paved road says to retry once that process finishes its commit, and never to delete the lockfile.
  - Release truncates the identity to empty before closing, so a reader sees an empty file once the lock is free, even while the releasing process lives on.
  - Holds never nest. A hold covers only git write calls on the main checkout plus the journal append and `rev-parse` that record them. It never spans an LLM call, a test or gate run, a worktree operation, or a wait on the control inbox.
- In: every git write sequence on the main checkout runs inside one commit-lock hold:
  - `tickets.intake`: the per-stem `add`, `commit`, `rev-parse` and intake journal append. Change the signature or its callers in `chupa/drain.py`, `chupa/serve.py`, `chupa/runner.py` and `chupa/__main__.py` as needed.
  - `merge.write_squash`: `merge --squash` through the recorded commit.
  - The records commit in `chupa/stages.py` (`chupa(<stem>): <kind>`), the rework and undo-rework commits in `chupa/daemon.py`, the confirmed and rejected commits in `chupa/runner.py`, both commits in `chupa/author.py`, the state commit in `chupa/serve.py`, and the retro commit in `chupa/retro.py`.
  - The autofix commit in `chupa/stages.py` is made in a ticket worktree and stays outside the commit lock.
- In: `chupa/__main__.py`:
  - `_review` no longer takes the engine lock. When the ticket directory has pending changes, it runs intake under the commit lock and then reviews the committed blob as today.
  - `_verdict`: when the engine lock is held and the stem has pending ticket changes, it first runs intake under the commit lock. If intake refuses that stem, it refuses with the intake findings and publishes no admission request. Otherwise it publishes the request as today.
- In: `chupa/observe.py` `snapshot()`:
  - A top-level string field `commitLock`: empty when `commit.lock` is missing, empty, or names a pid that is not alive. Otherwise `<verb> since <time> (pid <pid>)`, built exactly like the existing `lock` field: the same command-line verb rule, defaulting to `chupa`, and `clock(started_at)`. Factor the verb rule so both fields use it.
  - Row menus:
    - `chupaReview` is `on` for an open, valid row whether or not an engine runs. It is never `locked`.
    - `chupaConfirm` and `chupaReject` are `on` for a draft or held row whether or not it is committed or an engine runs.
    - `chupaRun` stays `locked` while an engine runs.
    - The box rows' `chupaTriage` and `chupaDismiss` are unchanged.
  - The existing `lock` and `engine` fields are unchanged.
- In: `vscode-chupa/media/view.js`: the header shows two labelled padlocks, `engine` from `snap.lock` and `commit` from `snap.commitLock`, before the unchanged counts. Each shows `🔒` when its field is non-empty and `🔓` otherwise, with the field (or `unlocked`) as its hover title. JavaScript only draws the two fields.
- In: documentation of the two locks:
  - In `docs/how-chupa-works.md`: the verb table's lock column for `review`, `confirm` and `reject`; the `chupa.lock` row of the state-files table; and a new `commit.lock` row next to it.
  - In `chupa/docs/host-running.md`: the "Stop serve before ..." sentence, which no longer lists `review`.
  - In `chupa/docs/host-contract.md`: the lockfile paragraph, which says that writes to main take `commit.lock` with a 60-second wait.
- Out: `triage`, `dismiss` and `migrate-box`, which write the Suggestion Box and keep the engine lock. No `commit` verb. `doctor`'s lock probe. The engine lock's refusal between `run`, `drain` and `serve`. The `engine` snapshot field and `chupa.engineRunning`. The `vscode-chupa/package.json` menu clauses.
- Out: the operator's own git commits in the main checkout, which cannot take the lock. They stay outside it, as they are today.

## Scope fence
- chupa/lockfile.py
- chupa/__main__.py
- chupa/tickets.py
- chupa/merge.py
- chupa/stages.py
- chupa/daemon.py
- chupa/runner.py
- chupa/author.py
- chupa/serve.py
- chupa/retro.py
- chupa/drain.py
- chupa/observe.py
- vscode-chupa/media/view.js
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- chupa/docs/host-contract.md
- tests/integration/test_lockfile.py
- tests/integration/test_review_command.py
- tests/integration/test_control_cli.py
- tests/integration/test_watch.py
- tests/integration/test_merge.py
- tests/integration/test_drain.py

## Acceptance criteria
1. `tests/integration/test_lockfile.py` covers the commit lock with fake clock and sleep seams:
   - While another descriptor holds `commit.lock`, acquire waits, and it succeeds once that descriptor releases before 60 seconds have passed. It does not refuse on first contention.
   - When the holder never releases, acquire raises at 60 seconds with a message naming the holder's pid. It neither waits forever nor acquires.
   - After release, `commit.lock` is empty, not the stale identity.
2. `tests/integration/test_review_command.py`: with `chupa.lock` held by a separate `Lockfile` and an edited ticket on disk, `review` approves, commits the edit (`main:` holds the new text), journals the verdict, and exits 0. It does not exit 2 with a lock refusal. With `commit.lock` held past the wait, `review` exits 2 naming `commit.lock`, and the ticket stays uncommitted.
3. `tests/integration/test_control_cli.py`: with `chupa.lock` held and an edited valid draft on disk, `confirm --yes` commits the ticket and prints `confirm submitted:`. With an edited invalid draft, it exits 2 with the intake finding and publishes no admission request.
4. `tests/integration/test_merge.py`: while another descriptor holds `commit.lock`, `write_squash` does not run `merge --squash` until the lock is released. A test proves it, for example by releasing the lock from the fake sleep, then asserting that no squash happened before the release.
5. `tests/integration/test_watch.py`: with a live engine lock holder:
   - An open valid row's `chupaReview` is `on`, not `locked`, and a dirty held row's `chupaConfirm` and `chupaReject` are `on`, not `off`. `chupaRun` stays `locked`, and pending box rows stay `locked` for triage and dismiss. Update the existing assertions that pinned `locked` and `off`.
   - `commitLock` is `""` with no `commit.lock` and `""` with an empty `commit.lock`. For a live holder whose command line is `python -m chupa review stem`, it is `review since <clock(started_at)> (pid N)`.
6. `./dev.py test tests/integration/test_lockfile.py tests/integration/test_review_command.py tests/integration/test_control_cli.py tests/integration/test_watch.py tests/integration/test_merge.py tests/integration/test_drain.py` exits 0.
7. `docs/how-chupa-works.md` has a `commit.lock` row in its state-files table, and `chupa/docs/host-running.md`'s "Stop serve before" sentence no longer names `review`.

## Verification
```
./dev.py test tests/integration/test_lockfile.py tests/integration/test_review_command.py tests/integration/test_control_cli.py tests/integration/test_watch.py tests/integration/test_merge.py tests/integration/test_drain.py
```

## Definition of rejected
- A second `run`, `drain` or `serve` can start while one holds `chupa.lock`.
- A commit-lock hold spans an LLM call, a test or gate run, or a worktree operation. Holds nest.
- The wait has no limit, or the limit is not 60 seconds.
- Any code deletes or steals a lockfile.
- `view.js` computes availability or parses the lock strings.
- `triage`, `dismiss` or `migrate-box` move off the engine lock, or a new `commit` verb is added.

## Time budget
- expected: 90m
- stuck: 180m
