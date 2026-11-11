---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- verb-lock-need-single-source

## Context
- chupa/observe.py::snapshot
- chupa/observe.py::uncommitted_tickets
- chupa/__main__.py::_review
- docs/how-chupa-works.md#2.1 Verbs
- tests/regress_shared_hold_rule.py

## On-demand
- tests/integration/test_watch.py

## Goal / Why
The Tickets view greys out a row's Review menu item whenever an engine (drain, serve, run) holds `.chupa/state/chupa.lock`, even though `chupa review` no longer needs that lock for a committed ticket. Since the `commit-lock` change (8a303f33), `_review` in `chupa/__main__.py` takes the writer lock only when `tickets/<stem>/` has pending changes, and `docs/how-chupa-works.md` documents that ("Reviews an unchanged committed ticket without the checkout lock"). But `snapshot` in `chupa/observe.py` still builds `chupaReview` as `available(open_section and valid)`, and `available` returns `"locked"` for every row while the engine is alive. So during an hours-long drain the operator cannot review a committed ticket from the extension, though the CLI verb would succeed. Evidence: `evidence/review-menu-evidence.txt`.

When this ticket is done, a valid queued or blocked row whose ticket is committed gets `chupaReview: "on"` while the engine is alive. A row with an uncommitted `ticket.md` still gets `"locked"` while the engine is alive.

## Scope in / Scope out
- In: the `chupaReview` entry of the row menu in `chupa/observe.py::snapshot`. It is `"off"` when the row is not open or not valid, as today. It is `"locked"` when the engine is alive and the row is not committed (`r["committed"]` is false). Otherwise it is `"on"`.
- In: the `tests/integration/test_watch.py` assertion that pins `chupaReview` to `"locked"` for the committed `ready` row while the engine is alive flips to `"on"`; add a case for a dirty open row, which stays `"locked"`.
- In: new carried reproducer `tests/regress_review_menu_committed_unlocked.py`.
- Out:
  - Every other menu entry (`chupaRun`, `chupaTriage`, `chupaDismiss`, `chupaConfirm`, `chupaReject`). Run, triage and dismiss still always take the writer lock.
  - The extension (`vscode-chupa/`): it already renders `"on"`, `"locked"` and `"off"` from the snapshot.
  - Aligning the snapshot's dirty test (`ticket.md` only) with `_review`'s (any file under `tickets/<stem>/`), and any shared declaration of which verbs need the writer lock. Ticket `verb-lock-need-single-source` owns both.
  - Reporting `.chupa/state/commit.lock` in the snapshot.

## Scope fence
- chupa/observe.py
- tests/integration/test_watch.py
- tests/regress_review_menu_committed_unlocked.py

## Acceptance criteria
1. `tests/integration/test_watch.py`, with `lock_holder` faked alive and `uncommitted_tickets` returning no dirty stems: the valid, committed, queued `ready` row has `menu["chupaReview"] == "on"`, not `"locked"`. Its `chupaRun` is still `"locked"`.
2. The same test, with `lock_holder` alive and `uncommitted_tickets` reporting an open valid row as dirty: that row has `menu["chupaReview"] == "locked"`, not `"on"`.
3. The same test, with `lock_holder` returning `None`: `chupaReview` is `"on"` for both the committed and the dirty open valid rows. The invalid row's `chupaReview` stays `"off"` in every case.
4. `tests/regress_review_menu_committed_unlocked.py` imports nothing from `tests/` and fakes the snapshot inputs the way `tests/integration/test_watch.py` does. It prints `pass` only when a committed open valid row gets `chupaReview == "on"` while the engine is alive. At base, where that row gets `"locked"`, it prints `defect`.
5. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- Review shows `"on"` for a row with an uncommitted `ticket.md` while the engine is alive.
- Any menu entry other than `chupaReview` changes value.
- The fix lives in `vscode-chupa/` JavaScript instead of the snapshot.

## Time budget
- expected: 20m
- stuck: 60m

## Regression
```
uv run python tests/regress_review_menu_committed_unlocked.py
```
- carries: tests/regress_review_menu_committed_unlocked.py
