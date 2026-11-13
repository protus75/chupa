---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- chupa/__main__.py::_order
- chupa/__main__.py::_lint
- chupa/triage.py::triage_pass
- chupa/triage.py::validate_ids
- chupa/triage.py::dismiss
- chupa/triage.py::_settle_pass
- chupa/status.py::last_states
- chupa/status.py::verdict_refusal
- chupa/reconcile.py::orphans
- chupa/observe.py::lock_holder
- tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire

## Goal / Why
This is the second of three successors of `menu-mirrors-verb-admission`. The goal is that a menu item is on exactly when its verb would act on the row, decided by one function shared by the verb and `snapshot`. This ticket extracts the existing refusal rules of `order`, `lint`, `triage`, and `dismiss` into pure admission functions in `chupa/status.py` and has each verb call its function. That module is where `verdict_refusal` already lives, and `chupa/observe.py` already imports it with no cycle. The later successor `menu-table-run-review-admission` builds the menu from these functions. This ticket changes no verb behavior.

## Scope in / Scope out
In:
- Add to `chupa/status.py` one small closed admission result (admit, a no-op with the verb's existing skip or "already ..." outcome, or a refusal with its message and paved road). Add pure admission functions for `order`, `lint`, `triage`, and `dismiss` that return it. They take their inputs as arguments (journal events, whether the ticket file exists, the lock holder, box messages) and do no disk, git, or process work.
- `order` admission covers only its stem-level rules, with today's messages: missing file; running unless orphaned (`reconcile.orphans`) with no lock holder; settled or rejected. `_order` keeps its stem-grammar and "no ordering option supplied" checks before admission, in today's order. Its edit-dependent refusals ("ticket ordering fields cannot be edited", "priority line cannot be edited", and `validate_ticket` on the edited text) stay in `_order` after admission, unchanged. So `order` admission admits a ticket that fails `validate_ticket`.
- `lint` admission: a stem whose ticket file is absent or escapes `tickets/` is a refusal, which `_lint` still prints as today's `no ticket file` line with exit 2, counted in the total. A settled or rejected stem is a no-op, which `_lint` skips, not counted in the valid/total summary. Every other stem is admitted. `_lint` keeps its `_intake_claims` use and never raises.
- `triage` and `dismiss` admission take box messages only. An unknown id is a refusal with the error `Box.get` raises today. A resolved message is a no-op: `dismiss` still prints `already resolved -> <link>` and exits 0, and `triage` still skips it. A pending message is admitted. Both run after the verb acquires the lock and runs `reap`, where `validate_ids` runs today. `tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire` keeps pinning that order.

Out:
- `run` and `review` admission, `chupa/observe.py`, the menu table, and docs: successor `menu-table-run-review-admission`.
- Any change to what these verbs accept, refuse, or skip, or to their messages or exit codes.

## Scope fence
- chupa/status.py
- chupa/__main__.py
- chupa/triage.py
- tests/unit/test_stale_running.py
- tests/unit/test_menu_admission.py

## Acceptance criteria
1. `tests/unit/test_menu_admission.py` calls each of the `order`, `lint`, `triage`, and `dismiss` admission functions directly, with journal events, file-existence flags, the lock holder, and box messages passed in (no disk, no process). It covers each function's admit, no-op, and refusal outcomes, including `order` admitting a ticket that fails `validate_ticket` and `order` admitting an orphaned running stem only when no lock holder is passed.
2. `tests/unit/test_menu_admission.py` drives `_order` in `chupa/__main__.py`, and `triage_pass` and `dismiss` in `chupa/triage.py`, with their journal, git, and box seams monkeypatched as `tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire` does. It asserts that each verb raises its admission's refusal with today's message, and that `dismiss` on a resolved message prints `already resolved` and exits 0.
3. `tests/unit/test_menu_admission.py` drives `_lint` with its journal, git `status_porcelain` and `git_common_dir`, the `tickets/` directory listing (`Path.iterdir`), and the ticket-path existence checks monkeypatched. It asserts the admission refusal surfaces as the existing `no ticket file` line with exit 2, and the no-op as a skipped stem not counted in the `lint: <valid>/<total> tickets valid` summary.
4. `tests/unit/test_stale_running.py::test_locked_verbs_reap_after_acquire` passes, asserting `dismiss` and `triage` admission runs after acquire and reap.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `order`, `lint`, `triage`, or `dismiss` accepts, refuses, or skips a stem or message it did not before this change, or changes a message or exit code.
- An admission function reads disk, git, the clock, or the lock file itself.
- Any file under `vscode-chupa/` or `chupa/observe.py` changes.

## Time budget
- expected: 60m
- stuck: 120m