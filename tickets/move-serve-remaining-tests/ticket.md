---
state: confirmed
source: human
priority: P3
kind: chore
---

## Depends on
- move-serve-lifecycle-kill-tests

## Context
- tests/integration/test_serve.py

## Goal / Why
`tests/integration/test_serve.py` is too large to embed in a ticket's `## Context`: `retro-request-serve` rendered 328,574 characters and `chupa review` refused it (2026-11-08). The split lands in three stages to stay under the 1,500-inserted-line diff budget. After `move-serve-rig` and `move-serve-lifecycle-kill-tests`, the helpers live in `tests/integration/serve_rig.py`, and the lifecycle, kill, and notification tests live in themed files. This final stage moves the remaining tests and deletes `test_serve.py`.

This is a pure move. No test's body, parameters, or assertions change.

## Scope in / Scope out
- In: move every remaining test unchanged from `test_serve.py` into new files. Each new file imports its helpers from `tests.integration.serve_rig`, and gets the `root` fixture and other imports the same way `test_serve.py` does.
  - `tests/integration/test_serve_admission.py`: `test_serve_routes_settled_run_to_composed_queue_once`, `test_serve_admission_rebases_regates_and_retires`, `test_serve_admission_holds_and_cleanup`, `test_serve_admission_refusal_keeps_main_green`, `test_serve_conflict_handoff_runs_after_admission_unwinds`.
  - `tests/integration/test_serve_upgrade.py`: `test_upgrade_after_real_merge`, `test_external_engine_change_at_admission`, `test_upgrade_waits_for_continuation`, `test_non_git_engine_disables_upgrade`, `test_kill_accepted_during_upgrade_cleanup_prevents_spawn`, `test_stop_finishes_merge_without_admitting_next_or_spawning`.
  - `tests/integration/test_serve_dispatch.py`: `test_refused_uncommitted_bug_does_not_stop_serve`, `test_dispatch_republishes_ticket_changed_after_publication`, `test_invalid_new_ticket_reaches_watcher`, `test_live_keep_dispatches_again_without_restart`, `test_serve_reoffers_failed_dispatch_with_machine_keep_and_retry`, `test_serve_premise_reoffer_draws_no_retry`, `test_serve_reoffers_merge_failure`, `test_requested_retro_waits_for_idle_then_resumes`, `test_kill_aborts_requested_retro`, `test_automatic_retro_runs_at_idle_when_due`, `test_automatic_retro_off_when_disabled`, `test_failed_retro_does_not_reblock`, and any other test still in `test_serve.py`.
- In: delete `tests/integration/test_serve.py`.
- Out:
  - any change to a test body, parametrization, or helper behavior;
  - any change to `serve_rig.py`, the files moved by the earlier stages, or a `chupa/` source file;
  - splitting `test_daemon_composition.py` or `test_drain.py`.

## Scope fence
- tests/integration/test_serve.py
- tests/integration/test_serve_admission.py
- tests/integration/test_serve_upgrade.py
- tests/integration/test_serve_dispatch.py

## Acceptance criteria
1. `tests/integration/test_serve.py` does not exist: `test ! -e tests/integration/test_serve.py`.
2. Every test that `tests/integration/test_serve.py` defined on the base commit is defined exactly once across the three new files, with the same name and parametrization. No test is lost, duplicated, or renamed: `rg -n "^(async )?def test_" tests/integration/test_serve_admission.py tests/integration/test_serve_upgrade.py tests/integration/test_serve_dispatch.py`.
3. Each new file is under 40,000 characters: `wc -c tests/integration/test_serve_admission.py tests/integration/test_serve_upgrade.py tests/integration/test_serve_dispatch.py`.
4. No file under `tests/` refers to `tests.integration.test_serve`: `rg -n "tests\.integration\.test_serve\b" tests --glob "*.py"`.
5. Tests pass: `./dev.py test`.

## Verification
```
./dev.py test tests/integration/test_serve_admission.py tests/integration/test_serve_upgrade.py tests/integration/test_serve_dispatch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a test body, parametrization, or assertion changed;
- a test from the base `test_serve.py` is missing or appears twice;
- a file outside `tests/integration/` changed.

## Time budget
- expected: 30m
- stuck: 120m