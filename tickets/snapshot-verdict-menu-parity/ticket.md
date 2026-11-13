---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- menu-mirrors-verb-admission

## Context
- chupa/observe.py::snapshot
- chupa/observe.py::held
- chupa/observe.py::operator_holds
- chupa/runner.py::verdict
- chupa/runner.py::verdict_locked
- chupa/runner.py::reject_ticket
- chupa/status.py::reject_queue
- chupa/status.py::last_states
- chupa/status.py::SETTLED
- chupa/reconcile.py::orphans
- chupa/drain.py::awaiting_operator
- tests/integration/test_watch.py::test_snapshot_menu_availability
- tests/integration/test_stale_running.py::test_menu_offers_reject_for_dead_run
- tests/regress_review_intakes_own_stem.py

## Goal / Why
The snapshot (the menu data the VS Code extension draws) and the `confirm`/`reject` verbs use different rules for which tickets accept a verdict, so the extension greys out verdicts the verb accepts and offers verdicts the verb refuses.

Observed 2026-11-13 in the fungo host on chupa 0.1.5 (`evidence/`): ticket `authoring-forced-edits-and-rule-tests` (state confirmed, section queued, status ready, never ran) had `"chupaReject": "off"`, yet `chupa reject <stem>` in a terminal accepts it. The only way to kill a queued ticket is the terminal.

Current code:
- `chupa/observe.py` `snapshot` sets `verdict = r["draft"] or r["held"]`, `chupaConfirm` on when `verdict`, `chupaReject` on when `verdict` or the row's last state is `running` and the stem is in `interrupted`.
- `chupa/runner.py` `verdict` reaps orphans (`reap` journals `abandoned` for each `orphans()` stem), then `verdict_locked`: refuses a last state of `running`; for kill, refuses a last state in `chupa.status.SETTLED` (`merged`, `already_satisfied`) and otherwise calls `reject_ticket`, which is an idempotent no-op ("already rejected", exit 0) on a rejected stem; for keep, accepts a `state: draft` ticket or a stem in `reject_queue(history)`, else refuses "neither a draft nor in the Reject queue".
- Confirm drifts both ways: the snapshot's `held` is `held(history, blobs) | operator_holds(...)`. `held` (a `parked_blob` content park) can hold a stem that is not in `reject_queue`, where the menu offers Confirm and the verb refuses; `operator_holds` is `awaiting_operator`, a strict subset of `reject_queue`, so a Reject-queue stem not awaiting the operator gets Confirm "off" while the verb accepts it.

Done means one decision function, called by both the verbs and the snapshot menu, decides whether confirm and reject are allowed for a stem, so the menu offers exactly the verdicts the verb accepts.

## Scope in / Scope out
In:
- Add one pure predicate (no I/O, no clock) in `chupa/status.py`, beside `reject_queue` and `last_states`, that takes the journal history, the stem, the verdict kind (keep or kill), whether the ticket is a draft, and the set of interrupted stems, and returns the refusal (message and paved road) or none. A stem in the interrupted set counts as not running, because `verdict` reaps it before deciding. `snapshot` passes its `interrupted` set (`orphans()` when no engine holds the lock, else empty). `verdict_locked` passes an empty set: `verdict` has already reaped, and under the engine (`apply_admission`) an `orphans()` stem is a live run.
- `verdict_locked` in `chupa/runner.py` calls it for the running, settled, draft, and Reject-queue rules and raises its refusal; keep the existing messages and paved roads. The unknown-stem check, the intake refusal, and the command-line-only same-content `prior_keep` refusal stay where they are (the extension passes `--extension`, which skips `prior_keep`).
- The `snapshot` menu in `chupa/observe.py` sets `chupaConfirm` and `chupaReject` from the same predicate, replacing `verdict = r["draft"] or r["held"]` and the interrupted special case. The `held` and `operator_holds` sets keep driving section placement and status text; they no longer drive the verdict menu.
- With today's verb rules, `chupaReject` is "on" for every snapshot row whose last state is not `running` (except an interrupted run) and not in `SETTLED`: queued, blocked, held, and draft rows. A rejected stem has no snapshot row (`RETIRED` excludes it), so it never shows a Reject item.
- `docs/how-chupa-works.md` section 2, the `vscode-chupa/` paragraph: add one sentence that the Confirm and Reject items are on exactly when the verb would accept them, decided by the shared predicate.

Out:
- `vscode-chupa/`: it draws only what the snapshot sends.
- The verb rules themselves (what may be confirmed or rejected); only the menu follows them.
- The TTY rule in `chupa/__main__.py`; the extension keeps using `--extension`.
- Menu items other than Confirm and Reject; ticket `menu-mirrors-verb-admission` covers them.

## Scope fence
- chupa/status.py
- chupa/runner.py
- chupa/observe.py
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/integration/test_stale_running.py
- tests/unit/test_verdict_menu_parity.py
- tests/regress_snapshot_verdict_menu_parity.py

## Acceptance criteria
1. `tests/unit/test_verdict_menu_parity.py` asserts a snapshot row for a confirmed, queued, never-run ticket has `chupaReject` "on", not "off".
2. `tests/unit/test_verdict_menu_parity.py` asserts `chupaReject` is "off" for a merged row and for a running row that is not interrupted (engine lock held), and that a rejected stem has no snapshot row.
3. `tests/unit/test_verdict_menu_parity.py` has a parity test over fixture stems in each state (draft, queued, blocked by a content park only, Reject queue awaiting the operator, Reject queue not awaiting the operator, running with the engine lock held, interrupted, merged). The oracle is the verdict's refusal, not the CLI exit code (with the engine lock held, `confirm`/`reject --extension` hand off and exit 0 whatever the outcome). With no engine lock, `chupaReject` is "on" exactly when `runner.verdict(stem, checkout, kill=True, extension=True)` returns without raising `Refusal`, and `chupaConfirm` likewise with `kill=False`. For the engine-held running fixture, each is "on" exactly when `runner.apply_admission(stem, verb, key, "extension", checkout)` returns `{"refusal": None}`. Both sides run against the same journal and ticket files; a test that checks only the menu or only the verb does not satisfy this criterion. A rejected stem is checked only by criterion 2 (no row).
4. `tests/unit/test_verdict_menu_parity.py` asserts `reject --extension` on a confirmed queued ticket stamps `state: rejected` in its `ticket.md`, commits it, and journals a `reject_verdict` signal with `verdict: kill` followed by a `state_transition` to `rejected`.
5. `tests/unit/test_verdict_menu_parity.py` asserts `runner.apply_admission(stem, "reject", key, "extension", checkout)` for a stem whose last transition is `running` (so it is in `orphans()`) returns a refusal containing `is running`, not `{"refusal": None}`.
6. `tests/integration/test_watch.py::test_snapshot_menu_availability` asserts `chupaConfirm` "off" for its content-parked `held` stem (not in the Reject queue), not today's "on", and asserts `chupaReject` "on" for the queued `ready` stem.
7. `observe.py`'s menu block contains no verdict rule of its own: `grep -n 'r\["held"\]' chupa/observe.py` finds no match in the `chupaConfirm`/`chupaReject` lines, and both lines call the predicate from `chupa/status.py`.
8. `uv run python tests/regress_snapshot_verdict_menu_parity.py` prints `{"regression_result": "pass"}` on the branch and `{"regression_result": "defect"}` at the merge base.
9. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- The snapshot computes Confirm or Reject availability with any rule not shared with `verdict_locked`.
- `confirm` or `reject` accepts or refuses a stem it did not accept or refuse before this change (the parity test passes because the verb moved toward the menu).
- The TTY rule for terminal `confirm`/`reject` is loosened.
- Any file under `vscode-chupa/` changes.

## Time budget
- expected: 45m
- stuck: 110m

## Regression
```
uv run python tests/regress_snapshot_verdict_menu_parity.py
```
- carries: tests/regress_snapshot_verdict_menu_parity.py
