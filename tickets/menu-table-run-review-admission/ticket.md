---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- snapshot-verdict-menu-parity
- intake-plan-helper
- verb-admission-order-lint-box

## Context
- chupa/observe.py::snapshot
- chupa/__main__.py::_review
- chupa/runner.py::_admit
- chupa/runner.py::ticket_pending
- chupa/runner.py::verdict_locked
- chupa/tickets.py::intake
- chupa/tickets.py::_pending
- chupa/status.py::verdict_refusal
- chupa/status.py::last_states
- vscode-chupa/extension.js
- tests/integration/test_watch.py::test_snapshot_menu_availability
- tests/integration/test_stale_running.py::test_menu_offers_reject_for_dead_run
- tests/unit/test_verdict_menu_parity.py
- tests/regress_review_menu_committed_unlocked.py
- tests/regress_snapshot_verdict_menu_parity.py
- tests/regress_engine_flag_only_drain_serve.py
- tests/regress_review_intakes_own_stem.py

## Goal / Why
This is the last of three successors of `menu-mirrors-verb-admission`. The VS Code extension must mirror what chupa allows: a menu item is on exactly when its verb would act on that row, decided by one function, so the menu and the verb cannot drift. Today every menu key in `snapshot` (`chupa/observe.py`) is a hand-written copy of its verb's rules, and the copies have drifted. Examples: `chupaReview` is off for a running row that `_review` accepts; `chupaPriority` and `chupaRunsBefore` are off for an interrupted running stem that `_order` accepts; `chupaLint` is on for settled rows that `_lint` skips; `chupaRun` uses the copied `runnable` field; `chupaTriage` and `chupaDismiss` copy a pending rule. `intake-plan-helper` extracts intake's decision. `verb-admission-order-lint-box` adds admission for `order`, `lint`, `triage`, and `dismiss`. This ticket adds `run` and `review` admission and builds every menu key from one closed table, so the next menu item or verb rule change cannot reintroduce drift.

## Scope in / Scope out
In:
- Add pure `run` and `review` admission functions to `chupa/status.py` beside the others, returning the same closed admission result. `_admit` in `chupa/runner.py` and `_review` in `chupa/__main__.py` call them and behave exactly as today on each outcome.
- `run` and `review` admission decide a pending stem by the result of the intake helper from `intake-plan-helper`, which the caller (verb or `snapshot`) computes and passes in. `snapshot` computes pending and new stems as intake and `_lint` do (`tickets._pending` over `tickets._porcelain`). For a non-pending stem, the caller passes `review` admission the result of `validate_ticket` on the committed `main:` text, as `_review` computes it today. `snapshot` computes it the same way and does not reuse `load_tickets`' `invalid` set. The caller passes `run` admission the result of `validate_ticket` (no `_settled`) on the on-disk text, as `_admit` computes it; for a pending stem that text is the helper's claimed (stamped) text. Both apply intake's stray-staged refusal (`IntakeRefused`) from the helper's stray paths. `run` applies it unconditionally. `review` applies it only when the stem has a porcelain entry under `tickets/<stem>/` (the `runner.ticket_pending` test), which the caller passes as a flag.
- `chupaConfirm` and `chupaReject` keep the predicate from `snapshot-verdict-menu-parity`, unchanged and not lock-gated.
- A closed table in `chupa/observe.py` maps every menu key the snapshot emits to its row kind (ticket or box), its verb's admission function, and whether that verb needs the writer lock (`run`, `triage`, `dismiss` do; `review`, `lint`, `order` do not). `chupaAskDiagnose` and `chupaAskReview` are extension-only entries, each carrying today's Ask rule unchanged. A key is "on" when admission returns admit, "locked" when it admits but needs the lock and an engine holds it, and "off" otherwise (a no-op is "off"). `snapshot` builds each ticket row's and box row's `menu` only by iterating that table's entries of the row's kind. Drop the row `runnable` field if nothing else reads it.
- `tests/unit/test_verdict_menu_parity.py` (its `world` fixture) and the carried regressions `tests/regress_review_menu_committed_unlocked.py`, `tests/regress_snapshot_verdict_menu_parity.py`, and `tests/regress_engine_flag_only_drain_serve.py` also supply the new snapshot inputs without git: the porcelain and intake-helper result, the `main:` text and `validate_ticket` results, and `ticket_pending`. Their assertions, pass/defect verdicts, and output stay unchanged.
- `docs/how-chupa-works.md` section 2, the `vscode-chupa/` paragraph: state that every verb-backed menu item is on exactly when its verb's admission function admits the row, through the table in `chupa/observe.py`, and that the Ask items are extension-only.

Out:
- `vscode-chupa/`: the snapshot's `menu` keys and values (`on`, `off`, `locked`) keep their names.
- Verb rules (what each verb accepts, refuses, or skips) and verb exit codes.
- The Ask items' availability rules.

## Scope fence
- chupa/observe.py
- chupa/__main__.py
- chupa/runner.py
- chupa/status.py
- chupa/tickets.py
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/integration/test_stale_running.py
- tests/unit/test_verdict_menu_parity.py
- tests/unit/test_menu_admission.py
- tests/regress_review_menu_committed_unlocked.py
- tests/regress_snapshot_verdict_menu_parity.py
- tests/regress_engine_flag_only_drain_serve.py
- tests/integration/test_menu_verb_parity.py

## Acceptance criteria
1. `tests/integration/test_menu_verb_parity.py` asserts a snapshot ticket row's menu key set equals the table's ticket-kind keys and a box row's menu key set equals its box-kind keys. It also asserts every key not marked extension-only maps to an admission function, so adding a menu key without one fails the test.
2. `tests/integration/test_menu_verb_parity.py` runs each verb-backed key's admission function and the snapshot on the same journal and files, for each of these fixture row states:
   - draft; new uncommitted draft; staged new draft; dirty committed
   - pending ticket with a lint finding; committed ticket that closes a depends cycle
   - committed confirmed ticket with settled depends whose Runs before closes a cycle
   - stray staged file outside `tickets/` with a clean committed row (review "on", run "off")
   - stray staged file with an untracked file under the row's `tickets/<stem>/` (review and run both "off")
   - pending ticket with a staged regular evidence file and nothing else staged (review and run admitted)
   - pending already_satisfied stem whose ticket fails the evidence check (`chupaRun` "off")
   - queued; blocked; content-parked; Reject queue; running with the lock held; interrupted; merged; invalid
   - pending and resolved box messages

   For every row it asserts the menu value is "on" or "locked" exactly when admission returns admit.
3. `tests/integration/test_menu_verb_parity.py` asserts `chupaReview` is not "off" for a running row, and `chupaDismiss` is "off" for a resolved message while `dismiss` on it still prints `already resolved` and exits 0.
4. `tests/integration/test_menu_verb_parity.py` asserts that with the engine lock held:
   - an admitted row's `chupaRun`, `chupaTriage`, and `chupaDismiss` are "locked";
   - its `chupaReview`, `chupaLint`, `chupaPriority`, and `chupaRunsBefore` are "on";
   - a draft row's `chupaConfirm` and `chupaReject` are "on".
5. `tests/unit/test_menu_admission.py` calls `run` and `review` admission directly with passed-in intake-helper results for a pending stem, a non-pending stem, and stray paths, and covers admit and refusal. It drives `_review` and `_admit` with journal and git seams monkeypatched and asserts each raises its admission's refusal with today's message. It also asserts `intake` and `snapshot` get the same helper result for a settled pending stem and for a pending stem with a staged regular evidence file, with git and file reads faked.
6. `tests/integration/test_menu_verb_parity.py` asserts each verb (`review`, `lint`, `run`, `order`, `triage`, `dismiss`) refuses with its existing message when its admission function refuses. With `tmp_path` ticket files, it asserts `lint` prints the `no ticket file` line with exit 2 for a refusal and skips a no-op stem in its valid/total summary.
7. `grep -n 'open_section\|r\["runnable"\]' chupa/observe.py` finds no match outside the table's extension-only Ask entries.
8. `./dev.py test` exits 0.

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