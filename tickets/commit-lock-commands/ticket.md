---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- commit-lock

## Context
- chupa/__main__.py::_review
- chupa/__main__.py::_verdict
- chupa/observe.py::lock_holder
- chupa/observe.py::snapshot
- vscode-chupa/media/view.js
- chupa/lockfile.py
- chupa/runner.py::verdict

## On-demand
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- tests/integration/test_review_command.py
- tests/integration/test_control_cli.py
- tests/integration/test_watch.py

## Goal / Why
After `commit-lock`, every git write takes the short commit lock inside `chupa/git.py`. `review`, `confirm` and `reject` still treat the engine lock (`chupa.lock`) as a reason to refuse or to hand off, and the tickets view still greys them out whenever an engine runs.

On 2026-11-10, `./dev.py review core-template-budget` and `./dev.py review commit-lock` were both refused after an edit while a drain ran, and each review had to wait for the drain to commit the edit first. The view also greys Review on committed tickets, even though reviewing them never needed the lock.

After this change:
- `review` on an edited ticket commits it and reviews it while a drain runs.
- `confirm` and `reject` on an edited ticket commit it before handing off to the running engine.
- The view enables those three actions whenever the row allows them.
- The view header shows both locks.

## Scope in / Scope out
- In: `chupa/__main__.py`:
  - `_review` never takes `chupa.lock`. When the ticket directory has pending changes, it runs intake, which waits on the commit lock inside `Git`, then reviews the committed blob as today.
  - `_verdict`: when `runner.verdict` finds `chupa.lock` held and the stem's ticket directory has pending changes, it runs intake first. If intake refuses that stem, the command exits 2 with the intake findings and publishes no admission request. Otherwise it publishes the request as today. A `CommitLockTimeout` exits 2 through the top-level handler, and no request is published.
- In: `chupa/observe.py` `snapshot()`:
  - New top-level string field `commitLock`. It is empty when `<state>/commit.lock` is missing, empty, or names a pid that is not alive. Otherwise it is `<verb> since <time> (pid <pid>)`, built exactly like the existing `lock` field. Factor the verb rule so both fields use it.
  - Row menus:
    - `chupaReview` is `on` for an open, valid row whether or not an engine runs, and is never `locked`.
    - `chupaConfirm` and `chupaReject` are `on` for a draft or held row whether or not it is committed or an engine runs.
    - `chupaRun` stays `locked` while an engine runs.
    - Box rows' `chupaTriage` and `chupaDismiss` are unchanged.
  - The `lock` and `engine` fields are unchanged.
- In: `vscode-chupa/media/view.js`: the header shows two labelled padlocks, `engine` from `snap.lock` and `commit` from `snap.commitLock`, before the unchanged counts. Each shows `🔒` when its field is non-empty and `🔓` otherwise, with the field, or `unlocked`, as its hover title. The JavaScript only draws the two fields.
- In: documentation:
  - In `docs/how-chupa-works.md`: the verb table's lock column and text for `review`, `confirm` and `reject`.
  - In `chupa/docs/host-running.md`: the "Stop serve before ..." sentence no longer names `review`. In the verb table's `review` row, the "Works while serve runs?" cell becomes `Yes`, and its description says a pending edit is committed through intake before the review.
- Out:
  - `triage`, `dismiss` and `migrate-box` keep the engine lock.
  - No `commit` verb.
  - No change to `vscode-chupa/package.json`, the `engine` field, or `chupa.engineRunning`.

## Scope fence
- chupa/__main__.py
- chupa/observe.py
- vscode-chupa/media/view.js
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- tests/integration/test_review_command.py
- tests/integration/test_control_cli.py
- tests/integration/test_watch.py
- tests/unit/test_verdict_extension.py

## Acceptance criteria
1. `tests/integration/test_review_command.py`:
   - With `chupa.lock` held by a separate `Lockfile` and an edited ticket on disk, `review` approves, commits the edit (`main:` holds the new text), journals the verdict, and exits 0. It does not exit 2 with a lock refusal.
   - With `commit.lock` held past the wait (fake clock and sleep), `review` exits 2 naming `commit.lock`, and the ticket stays uncommitted.
2. `tests/integration/test_control_cli.py`:
   - With `chupa.lock` held and an edited valid draft, `confirm --yes` commits the ticket and prints `confirm submitted:`.
   - With an edited invalid draft, it exits 2 with the intake finding and publishes no admission request.
   - With `commit.lock` held past the wait, it exits 2 naming `commit.lock` and publishes no admission request.
3. `tests/integration/test_watch.py`, with a live engine lock holder:
   - An open valid row's `chupaReview` is `on`, not `locked`.
   - A dirty held row's `chupaConfirm` and `chupaReject` are `on`, not `off`.
   - `chupaRun` stays `locked`, and pending box rows stay `locked` for triage and dismiss. Update the existing assertions that pinned `locked` and `off`.
   - `commitLock` is `""` with no `commit.lock`, and `""` with an empty one.
   - For a live holder whose command line is `python -m chupa review stem`, `commitLock` is `review since <clock(started_at)> (pid N)`.
4. `tests/unit/test_verdict_extension.py` keeps the `chupa/__main__.py` unit floor. With `runner.verdict` raising `LockHeld` and a fake git reporting pending changes for the stem:
   - A refused intake raises `Refusal`, and `control.publish_request` is never called.
   - A clean intake publishes exactly one request.
5. `./dev.py test tests/unit/test_verdict_extension.py tests/integration/test_review_command.py tests/integration/test_control_cli.py tests/integration/test_watch.py` exits 0.
6. In `chupa/docs/host-running.md`, the "Stop serve before" sentence no longer names `review`, and the verb table's `review` row says `Yes` under "Works while serve runs?".

## Verification
```
./dev.py test tests/unit/test_verdict_extension.py tests/integration/test_review_command.py tests/integration/test_control_cli.py tests/integration/test_watch.py
```

## Definition of rejected
- `review` takes `chupa.lock`.
- `confirm` or `reject` publishes an admission request after intake refused the stem or the commit lock timed out.
- `view.js` computes availability or parses the lock strings.
- `triage`, `dismiss` or `migrate-box` move off the engine lock.

## Time budget
- expected: 60m
- stuck: 120m
