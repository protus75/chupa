---
state: confirmed
source: human
priority: P3
kind: chore
---

## Depends on
- none

## Context
- tests/integration/test_serve.py

## On-demand
- tests/integration/test_watchdog_activation.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_kill_worker_stop.py
- tests/integration/test_merge.py
- tests/integration/test_daemon_tasks.py
- tests/integration/test_hostfiles.py
- tests/integration/test_heartbeat.py
- tests/integration/test_provider_cooldown_failover.py
- tests/integration/test_kill_failure_suppression.py
- tests/integration/test_checkpoint.py

## Goal / Why
`tests/integration/test_serve.py` is 95,421 characters and holds 50 tests because every serve ticket appends to it. A ticket that embeds it in `## Context` spends a third of the 300,000-character authoring headroom on one file: `retro-request-serve` rendered 328,574 characters and `chupa review` refused it (2026-11-08). Moving the whole split in one diff exceeds the 1,500-inserted-line diff budget, so it lands in three stages. This first stage moves the shared rig into one helper module and points every importer at it.

This is a pure move. No helper's name or body changes, and no test changes.

## Scope in / Scope out
- In: create `tests/integration/serve_rig.py` and move into it every module-level helper and class of `test_serve.py` that is not a test: `until`, `graph`, `write`, `script`, `terminals`, `request`, `trip`, `finish`, `activated_graph`, `HeldLLM`, `active_graph`, `admission_graph`, `admission_ticket`, `start_admission`, `admission_config`, `notify_command`, `deliveries`, `notify_completions`, `escalation_batch`, `UpgradeChild`, `enable_upgrade`, and `retro_scenario`. Keep their names and bodies unchanged. Give `serve_rig.py` the imports its helpers need.
- In: in `test_serve.py`, delete the moved definitions and import them from `tests.integration.serve_rig`. Drop imports that become unused. Keep the `root` fixture import that the tests need.
- In: change the `from tests.integration.test_serve import ...` lines in `test_watchdog_activation.py`, `test_daemon_composition.py`, `test_kill_worker_stop.py`, `test_merge.py`, `test_daemon_tasks.py`, `test_hostfiles.py`, `test_heartbeat.py`, `test_provider_cooldown_failover.py`, `test_kill_failure_suppression.py`, and `test_checkpoint.py` to import from `tests.integration.serve_rig`.
- Out:
  - moving any test out of `test_serve.py` (later stages `move-serve-lifecycle-kill-tests` and `move-serve-remaining-tests`);
  - any change to a test body, parametrization, or helper behavior;
  - any `chupa/` source file.

## Scope fence
- tests/integration/test_serve.py
- tests/integration/serve_rig.py
- tests/integration/test_watchdog_activation.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_kill_worker_stop.py
- tests/integration/test_merge.py
- tests/integration/test_daemon_tasks.py
- tests/integration/test_hostfiles.py
- tests/integration/test_heartbeat.py
- tests/integration/test_provider_cooldown_failover.py
- tests/integration/test_kill_failure_suppression.py
- tests/integration/test_checkpoint.py

## Acceptance criteria
1. `tests/integration/serve_rig.py` defines every helper listed in Scope in, and `tests/integration/test_serve.py` defines none of them: `rg -n "^(async )?def |^class " tests/integration/serve_rig.py tests/integration/test_serve.py`.
2. `tests/integration/test_serve.py` still defines the same 50 test functions as on the base commit: `rg -c "^(async )?def test_" tests/integration/test_serve.py`.
3. `tests/integration/serve_rig.py` is under 40,000 characters: `wc -c tests/integration/serve_rig.py`.
4. No file under `tests/` imports from `tests.integration.test_serve`: `rg -n "tests\.integration\.test_serve import" tests --glob "*.py"`.
5. Tests pass: `./dev.py test`.

## Verification
```
./dev.py test tests/integration/test_serve.py tests/integration/test_watchdog_activation.py tests/integration/test_daemon_composition.py tests/integration/test_kill_worker_stop.py tests/integration/test_merge.py tests/integration/test_daemon_tasks.py tests/integration/test_hostfiles.py tests/integration/test_heartbeat.py tests/integration/test_provider_cooldown_failover.py tests/integration/test_kill_failure_suppression.py tests/integration/test_checkpoint.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a test or helper body, parametrization, or assertion changed;
- a test left `test_serve.py`;
- a file outside `tests/integration/` changed.

## Time budget
- expected: 30m
- stuck: 120m