---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- snapshot-verdict-menu-parity

## Context
- chupa/observe.py::snapshot
- chupa/__main__.py::_review
- chupa/__main__.py::_lint
- chupa/__main__.py::_order
- chupa/runner.py::_admit
- chupa/runner.py::run_ticket
- chupa/runner.py::verdict_locked
- chupa/triage.py::triage_pass
- chupa/triage.py::validate_ids
- chupa/triage.py::dismiss
- chupa/tickets.py::intake
- chupa/tickets.py::_pending
- chupa/status.py::last_states
- chupa/reconcile.py::orphans
- vscode-chupa/extension.js
- tests/integration/test_watch.py::test_snapshot_menu_availability
- tests/integration/test_stale_running.py::test_menu_offers_reject_for_dead_run
- tests/regress_review_intakes_own_stem.py

## Goal / Why
The VS Code extension must be a mirror of what chupa allows: a menu item is on exactly when its verb would act on that row, decided by one function, so the menu and the verb cannot drift. Today every menu key in `snapshot` (`chupa/observe.py`) is a hand-written copy of its verb's rules, and the copies have drifted (`evidence/`). Ticket `snapshot-verdict-menu-parity` fixes Confirm and Reject; this ticket removes the cause for every other verb-backed item, so the next menu item or verb rule change cannot reintroduce the drift.

Drift found in the current code:
- `chupaReview` is on only for queued and blocked valid rows; `_review` refuses only settled, rejected, missing, or invalid tickets, so it accepts a running row the menu greys out.
- `chupaPriority` and `chupaRunsBefore` are on only for queued and blocked valid rows; `_order` also accepts an interrupted running stem (orphaned, no lock holder).
- `chupaLint` is on for every non-merged row; `_lint` with a named settled or rejected stem skips it and exits 0.
- `chupaRun` uses the row's `runnable` field, a copy of `_admit`'s confirmed and dependencies-settled rules commented "What `chupa run` accepts".
- `chupaDismiss` is on only for pending messages; `dismiss` on a resolved message prints "already resolved" and exits 0. `chupaTriage` copies the same pending rule.

## Scope in / Scope out
In:
- For each verb behind a ticket-row or Suggestion Box menu item (`review`, `lint`, `run`, `order` for Priority and Runs before, `triage`, `dismiss`; `confirm` and `reject` already use the predicate from `snapshot-verdict-menu-parity`), extract its existing refusal rules into one admission function that returns admit, a no-op (the verb's existing "already ..." or skip outcome), or a refusal with its message and paved road. The verb calls that function before acting and behaves exactly as today on each outcome. Admission functions are pure over the journal, ticket files, and lock holder they are given; the verb and `snapshot` pass the same inputs. Place them where `snapshot` can import them without an `observe` <-> `__main__` import cycle (`chupa/status.py`, `chupa/runner.py`, or `chupa/triage.py`).
- Only verbs that intake model intake. `run` and `review` admission decide a pending stem by intake's own decision, because both intake before deciding (intake stamps a new human `state: draft` ticket `confirmed`). Extract from `intake` in `chupa/tickets.py` a non-committing helper that, given the porcelain entries and the per-stem evidence path listings, returns the stray staged paths (staged outside the pending ticket files and their regular evidence files, intake's `allowed` rule) and, for each pending stem, the claimed text and its findings or validated ticket (including the `_settled=True` handling for settled or rejected stems). `intake` keeps committing on top of that helper's result; `snapshot` calls the same helper, never a copy of its rules. Those checks read the repo, so the caller (verb or `snapshot`) runs the helper and passes its result into the admission function, which stays pure and only decides admit, no-op, or refusal. `snapshot` computes which stems are pending and new the way intake and `_lint` do (`tickets._pending` over `tickets._porcelain`), so an index-added ticket counts as new on both sides. For a non-pending stem, the caller passes `review` admission the result of `validate_ticket` on the committed `main:` text (the validated ticket or its findings), as `_review` computes it today; `snapshot` computes it the same way and does not reuse `load_tickets`' `invalid` set, which misses cycle findings. Likewise, the caller passes `run` admission the result of `validate_ticket` (no `_settled`) on the on-disk text, as `_admit` computes it, never `load_tickets`. For a pending stem it runs on the helper's claimed (stamped) text and is passed alongside the helper's decision, because `_admit` re-validates after intake. `run` and `review` admission also apply intake's repo-wide stray-staged refusal (`IntakeRefused`), taking the stray paths from the shared helper. `run` admission applies it unconditionally, as `_admit` always intakes. `review` admission applies it only when the stem has a porcelain entry under `tickets/<stem>/` (the `runner.ticket_pending` test `_review` uses today, which also counts evidence-only changes); the caller passes that flag alongside the stray paths. `lint` keeps its existing `_intake_claims` use. `order` admission reads the on-disk text as `_order` does. `triage` and `dismiss` admission take box messages only.
- `order` admission covers only its stem-level rules: missing file, running unless orphaned with no lock holder, settled or rejected. `_order` keeps its stem-grammar and "no ordering option supplied" checks before admission, in today's order. Its edit-dependent refusals ("ticket ordering fields cannot be edited", "priority line cannot be edited", and `validate_ticket` on the edited text) stay in `_order` after admission, unchanged. A row in the snapshot's `invalid` set is therefore "on" for Priority and Runs before, and `_order` decides the edit as it does today.
- `chupaConfirm` and `chupaReject` take their availability from the predicate added by `snapshot-verdict-menu-parity`, unchanged, and their table entries are not lock-gated: with the lock held, `confirm`/`reject` hand off to the running engine instead of refusing.
- The `dismiss` and `triage` admission runs after the verb acquires the lock and runs `reap`, where `validate_ids` runs today; `tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire` pins that order.
- A menu key is "on" exactly when its verb's admission function returns admit, "locked" when it admits but the verb needs the writer lock and an engine holds it, and "off" otherwise. A no-op is "off": the menu offers only actions the verb would perform. Today `run`, `triage`, and `dismiss` take the writer lock; `review`, `lint`, and `order` do not.
- A closed table in `chupa/observe.py` maps every menu key the snapshot emits to its row kind (ticket or box), its verb's admission function, and whether that verb needs the writer lock, or to an extension-only entry for `chupaAskDiagnose` and `chupaAskReview`, which run no chupa verb (they open a Claude chat). An extension-only entry carries its own availability predicate, today's Ask rule moved into the table entry unchanged. `snapshot` builds each ticket row's and box row's `menu` only by iterating that table's entries of the row's kind and holds no availability rule outside it; drop the row `runnable` field if nothing else reads it.
- `tests/unit/test_verdict_menu_parity.py`: its `world` fixture also fakes the new snapshot inputs (the porcelain/intake-helper result, the `main:` text and `validate_ticket` results, and `ticket_pending`), so `snapshot` runs without git; its Confirm/Reject assertions stay unchanged.
- The carried regressions `tests/regress_review_menu_committed_unlocked.py`, `tests/regress_snapshot_verdict_menu_parity.py`, and `tests/regress_engine_flag_only_drain_serve.py` build snapshot contexts without git: each also supplies the new snapshot inputs (the porcelain/intake-helper result, the `main:` text and `validate_ticket` results, and `ticket_pending`) and keeps its existing pass/defect verdict and output unchanged.
- `docs/how-chupa-works.md` section 2, the `vscode-chupa/` paragraph: state that every verb-backed menu item is on exactly when its verb's admission function admits the row, through the table in `chupa/observe.py`, and that the Ask items are extension-only.

Out:
- `vscode-chupa/`: the snapshot's `menu` keys and values (`on`, `off`, `locked`) keep their names, so the extension is unchanged.
- Verb rules (what each verb accepts, refuses, or skips) and verb exit codes.
- The Ask items' availability rules (no chupa verb behind them); they move into the table unchanged.

## Scope fence
- chupa/observe.py
- chupa/__main__.py
- chupa/runner.py
- chupa/triage.py
- chupa/status.py
- chupa/tickets.py
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/integration/test_stale_running.py
- tests/unit/test_stale_running.py
- tests/unit/test_verdict_menu_parity.py
- tests/regress_review_menu_committed_unlocked.py
- tests/regress_snapshot_verdict_menu_parity.py
- tests/regress_engine_flag_only_drain_serve.py
- tests/unit/test_menu_admission.py
- tests/integration/test_menu_verb_parity.py
- tests/regress_menu_mirrors_verb_admission.py

## Acceptance criteria
1. `tests/integration/test_menu_verb_parity.py` asserts a snapshot ticket row's menu key set equals the table's ticket-kind keys and a box row's menu key set equals its box-kind keys, and that every key not marked extension-only maps to an admission function, so adding a menu key without one fails the test.
2. `tests/integration/test_menu_verb_parity.py` runs, for each verb-backed key and each fixture row state (draft, new uncommitted draft, staged new draft, dirty committed, pending ticket with a lint finding, committed ticket that closes a depends cycle, committed confirmed ticket with settled depends whose Runs before closes a cycle, a stray staged file outside `tickets/` with a clean committed row (review "on", run "off"), a stray staged file with an untracked file under the row's `tickets/<stem>/` (review and run both "off"), a pending ticket with a staged regular evidence file and nothing else staged (review and run admitted), a pending already_satisfied stem whose ticket fails the evidence check (run refused with `_admit`'s "is invalid" message, `chupaRun` "off"), queued, blocked, content-parked, Reject queue, running with the lock held, interrupted, merged, invalid; pending and resolved box messages), the verb's admission function and the snapshot on the same journal and files, and asserts the menu value is "on" or "locked" exactly when admission returns admit. A test that checks only the menu or only the verb does not satisfy this criterion.
3. `tests/integration/test_menu_verb_parity.py` asserts `chupaReview` is not "off" for a running row, not today's "off", and that `chupaDismiss` is "off" for a resolved message while `dismiss` on it still prints "already resolved" and exits 0.
4. `tests/integration/test_menu_verb_parity.py` asserts that with the engine lock held, an admitted row's `chupaRun`, `chupaTriage`, and `chupaDismiss` are "locked", its `chupaReview`, `chupaLint`, `chupaPriority`, and `chupaRunsBefore` are "on", not "locked", and a draft row's `chupaConfirm` and `chupaReject` are "on", not "locked".
5. `tests/unit/test_menu_admission.py` asserts `intake` and `snapshot` get the same result from the helper extracted from `intake` (stray paths, claimed text, findings) for a settled pending stem and for a pending stem with a staged regular evidence file, with git and file reads faked. It also calls each admission function directly with journal events, ticket text, and box messages passed in (no disk, no process) and covers its admit, no-op, and refusal outcomes, including `order` admitting an invalid ticket and the `run`/`review` decision on passed-in intake results for a pending stem. It also drives each refusing verb's admission call site (`_review` and `_order` in `chupa/__main__.py`; `_admit` in `chupa/runner.py`; `triage_pass` and `dismiss` in `chupa/triage.py`) with fakes (journal, git, and box seams monkeypatched as `tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire` does) and asserts the verb raises the admission's refusal. `_lint` never raises: `tests/unit/test_menu_admission.py` drives its admission call site with fakes (journal, git `status_porcelain` and `git_common_dir`, the `tickets/` directory listing (`Path.iterdir`), and the ticket-path existence checks monkeypatched), and `tests/integration/test_menu_verb_parity.py` repeats it with `tmp_path` ticket files, that its admission refusal surfaces as the existing `no ticket file` line with exit 2 and its no-op as a skipped stem not counted in the valid/total summary.
6. `tests/integration/test_menu_verb_parity.py` asserts each verb (`review`, `lint`, `run`, `order`, `triage`, `dismiss`) refuses with its existing message when its admission function refuses, so the verbs' accepted and refused sets are unchanged.
7. The `r["menu"]` and box `menu` assignments in `chupa/observe.py` are built only by iterating the table: `grep -n 'open_section\|r\["runnable"\]' chupa/observe.py` finds no match outside the table's extension-only Ask entries.
8. `uv run python tests/regress_menu_mirrors_verb_admission.py` prints exactly one JSON object and nothing else on stdout: `{"regression_result": "pass"}` with exit 0 on the branch, and `{"regression_result": "defect"}` with a nonzero exit at the merge base, reproducing `chupaReview` "off" for a running row. It drives only `observe.snapshot` (no import of the new admission functions or table), so it runs unchanged at the merge base.
9. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- Any menu key the snapshot emits is computed by a rule not shared with its verb.
- A verb accepts, refuses, or skips a stem or message it did not before this change, or changes its exit code.
- Any file under `vscode-chupa/` changes, or a snapshot `menu` key or value is renamed.

## Time budget
- expected: 90m
- stuck: 180m

## Regression
```
uv run python tests/regress_menu_mirrors_verb_admission.py
```
- carries: tests/regress_menu_mirrors_verb_admission.py
