---
state: confirmed
source: human
priority: P3
kind: chore
---

## Depends on
- move-serve-rig

## Context
- tests/integration/test_serve.py

## Goal / Why
`tests/integration/test_serve.py` is too large to embed in a ticket's `## Context`: `retro-request-serve` rendered 328,574 characters and `chupa review` refused it (2026-11-08). The split lands in three stages to stay under the 1,500-inserted-line diff budget. After `move-serve-rig`, the shared helpers live in `tests/integration/serve_rig.py`. This second stage moves the lifecycle, kill, and notification tests into themed files.

This is a pure move. No test's body, parameters, or assertions change.

## Scope in / Scope out
- In: move these tests unchanged from `test_serve.py` into new files. Each new file imports its helpers from `tests.integration.serve_rig`, and gets the `root` fixture and other imports the same way `test_serve.py` does.
  - `tests/integration/test_serve_lifecycle.py`: `test_serve_waits_at_quiescence_and_discovers_work`, `test_empty_box_report_intake`, `test_report_consumer_is_sequential`, `test_serve_cli_uses_production_composition`, `test_serve_holds_lock_through_cleanup`, `test_serve_startup_precedes_all_work`, `test_serve_recovery_refusal_starts_no_work`, `test_serve_control_precedes_offer_accounting`, `test_serve_recurring_maintenance_uses_injected_time`, `test_serve_heartbeat_requires_responsive_components`, `test_serve_consumers_use_existing_writers`, `test_serve_watcher_edits_deletions_and_last_good`, `test_serve_control_stop_lifecycle_log`.
  - `tests/integration/test_serve_kill.py`: `test_serve_worker_failure_and_kill_suppression`, `test_serve_storm_suspends_stage_and_frees_selection`, `test_serve_storm_hold_and_resume`, `test_serve_kill_unwinds_executor_before_workers`, `test_serve_signal_stop_and_restart_recovery`, `test_serve_storm_resume_retains_producing_run`, `test_serve_suspended_run_cleanup_and_restart`, `test_serve_kill_unwinds_check_cleanup`, `test_serve_kill_unwinds_preparation`, `test_serve_abort_failure_does_not_apply_kill`.
  - `tests/integration/test_serve_notify.py`: `test_serve_reconciles_notifications_at_startup_and_poll`, `test_serve_unset_notify_warns_once_and_preserves_pending`, `test_serve_failed_notify_backoff_and_restart`, `test_serve_hung_notify_keeps_maintenance_and_cleanup_responsive`.
- In: delete the moved tests from `test_serve.py` and drop imports that become unused there.
- Out:
  - the admission, upgrade, and remaining tests, and deleting `test_serve.py` (stage `move-serve-remaining-tests`);
  - any change to a test body, parametrization, or helper behavior;
  - any change to `serve_rig.py` or a `chupa/` source file.

## Scope fence
- tests/integration/test_serve.py
- tests/integration/test_serve_lifecycle.py
- tests/integration/test_serve_kill.py
- tests/integration/test_serve_notify.py

## Acceptance criteria
1. Each of the 27 tests listed in Scope in is defined exactly once, in its named file, with the same name and parametrization, and is no longer defined in `test_serve.py`: `rg -n "^(async )?def test_" tests/integration/test_serve.py tests/integration/test_serve_lifecycle.py tests/integration/test_serve_kill.py tests/integration/test_serve_notify.py`.
2. `tests/integration/test_serve.py` still defines the other 23 tests from the base commit: `rg -c "^(async )?def test_" tests/integration/test_serve.py`.
3. Each new file is under 40,000 characters: `wc -c tests/integration/test_serve_lifecycle.py tests/integration/test_serve_kill.py tests/integration/test_serve_notify.py`.
4. Tests pass: `./dev.py test`.

## Verification
```
./dev.py test tests/integration/test_serve.py tests/integration/test_serve_lifecycle.py tests/integration/test_serve_kill.py tests/integration/test_serve_notify.py
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