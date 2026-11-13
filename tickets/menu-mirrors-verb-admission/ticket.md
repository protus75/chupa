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
- Each admission function evaluates a pending ticket's text as intake would leave it, by applying `_intake_claims(stem, text, new)` the way `_lint` already does, because `run` and `review` intake before deciding (intake stamps a new human `state: draft` ticket `confirmed`). `snapshot` passes its `new` and `dirty` sets (from `uncommitted_tickets`) as that input.
- The `dismiss` and `triage` admission runs after the verb acquires the lock and runs `reap`, where `validate_ids` runs today; `tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire` pins that order.
- A menu key is "on" exactly when its verb's admission function returns admit, "locked" when it admits but the verb needs the writer lock and an engine holds it, and "off" otherwise. A no-op is "off": the menu offers only actions the verb would perform. Today `run`, `triage`, and `dismiss` take the writer lock; `review`, `lint`, and `order` do not.
- A closed table in `chupa/observe.py` maps every menu key the snapshot emits to its verb's admission function and whether that verb needs the writer lock, or to an extension-only entry for `chupaAskDiagnose` and `chupaAskReview`, which run no chupa verb (they open a Claude chat). An extension-only entry carries its own availability predicate, today's Ask rule moved into the table entry unchanged. `snapshot` builds every row and box `menu` only by iterating that table and holds no availability rule outside it; drop the row `runnable` field if nothing else reads it.
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
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/integration/test_stale_running.py
- tests/unit/test_stale_running.py
- tests/unit/test_menu_verb_parity.py
- tests/regress_menu_mirrors_verb_admission.py

## Acceptance criteria
1. `tests/unit/test_menu_verb_parity.py` asserts the set of menu keys in a snapshot ticket row and box row equals the key set of the table in `chupa/observe.py`, and that every key not marked extension-only maps to an admission function, so adding a menu key without one fails the test.
2. `tests/unit/test_menu_verb_parity.py` runs, for each verb-backed key and each fixture row state (draft, new uncommitted draft, dirty committed, queued, blocked, content-parked, Reject queue, running with the lock held, interrupted, merged, invalid; pending and resolved box messages), the verb's admission function and the snapshot on the same journal and files, and asserts the menu value is "on" or "locked" exactly when admission returns admit. A test that checks only the menu or only the verb does not satisfy this criterion.
3. `tests/unit/test_menu_verb_parity.py` asserts `chupaReview` is not "off" for a running row, not today's "off", and that `chupaDismiss` is "off" for a resolved message while `dismiss` on it still prints "already resolved" and exits 0.
4. `tests/unit/test_menu_verb_parity.py` asserts that with the engine lock held, an admitted row's `chupaRun`, `chupaTriage`, and `chupaDismiss` are "locked", and its `chupaReview`, `chupaLint`, `chupaPriority`, and `chupaRunsBefore` are "on", not "locked".
5. `tests/unit/test_menu_verb_parity.py` asserts each verb (`review`, `lint`, `run`, `order`, `triage`, `dismiss`) refuses with its existing message when its admission function refuses, so the verbs' accepted and refused sets are unchanged.
6. The `r["menu"]` and box `menu` assignments in `chupa/observe.py` are built only by iterating the table: `grep -n 'open_section\|r\["runnable"\]' chupa/observe.py` finds no match outside the table's extension-only Ask entries.
7. `uv run python tests/regress_menu_mirrors_verb_admission.py` prints `{"regression_result": "pass"}` on the branch and `{"regression_result": "defect"}` at the merge base, reproducing `chupaReview` "off" for a running row whose `review` the verb admits.
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

## Regression
```
uv run python tests/regress_menu_mirrors_verb_admission.py
```
- carries: tests/regress_menu_mirrors_verb_admission.py
