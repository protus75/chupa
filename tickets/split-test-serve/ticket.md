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
`tests/integration/test_serve.py` is 95,421 characters and holds 45 tests because every serve ticket appends to it. A ticket that embeds it in `## Context` spends a third of the 300,000-character authoring headroom on one file: `retro-request-serve` rendered 328,574 characters and `chupa review` refused it (2026-11-08). After this change the serve tests live in themed files, each small enough to embed, and the shared rig lives in one helper module.

This is a pure move. No test's body, parameters, or assertions change.

## Scope in / Scope out
- In: create `tests/integration/serve_rig.py` and move into it every module-level helper, fixture, and class of `test_serve.py` that is not a test, for example `until`, `graph`, `write`, `script`, `terminals`, `request`, `trip`, `finish`, `activated_graph`, `HeldLLM`, `active_graph`, `admission_graph`, `admission_ticket`, `start_admission`, `admission_config`, the notify helpers, `UpgradeChild`, and `enable_upgrade`. Keep their names and bodies unchanged.
- In: move every test from `test_serve.py` unchanged into one of these files. Each file imports what it needs from `serve_rig`.
  - `test_serve_lifecycle.py`: startup, lock, recovery, control ordering, intake, watcher, heartbeat, maintenance, consumers, and stop-lifecycle tests.
  - `test_serve_kill.py`: kill, signal, storm, abort, and worker-failure tests.
  - `test_serve_admission.py`: merge-queue admission, refusal, and conflict-handoff tests.
  - `test_serve_notify.py`: notification tests.
  - `test_serve_upgrade.py`: self-upgrade tests and the stop-during-merge test.
  - `test_serve_dispatch.py`: re-offer, live keep, republish, and every other test.
- In: delete `tests/integration/test_serve.py`.
- In: change the `from tests.integration.test_serve import ...` lines in `test_watchdog_activation.py`, `test_daemon_composition.py`, `test_kill_worker_stop.py`, `test_merge.py`, `test_daemon_tasks.py`, `test_hostfiles.py`, `test_heartbeat.py`, `test_provider_cooldown_failover.py`, `test_kill_failure_suppression.py`, and `test_checkpoint.py` to import from `tests.integration.serve_rig`.
- Out:
  - any change to a test body, parametrization, or helper behavior;
  - any `chupa/` source file;
  - splitting `test_daemon_composition.py` or `test_drain.py`.

## Scope fence
- tests/integration/test_serve.py
- tests/integration/serve_rig.py
- tests/integration/test_serve_lifecycle.py
- tests/integration/test_serve_kill.py
- tests/integration/test_serve_admission.py
- tests/integration/test_serve_notify.py
- tests/integration/test_serve_upgrade.py
- tests/integration/test_serve_dispatch.py
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
1. `tests/integration/test_serve.py` does not exist.
2. Every test function defined in `tests/integration/test_serve.py` on the base commit is defined exactly once across the six new `tests/integration/test_serve_*.py` files, with the same name and parametrization. No test is lost, duplicated, or renamed.
3. Each new `tests/integration/test_serve_*.py` file and `tests/integration/serve_rig.py` is under 40,000 characters.
4. No file under `tests/` imports from `tests.integration.test_serve`.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_serve_lifecycle.py tests/integration/test_serve_kill.py tests/integration/test_serve_admission.py tests/integration/test_serve_notify.py tests/integration/test_serve_upgrade.py tests/integration/test_serve_dispatch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a test body, parametrization, or assertion changed;
- a test from the base `test_serve.py` is missing or appears twice;
- a file outside `tests/integration/` changed.

## Time budget
- expected: 60m
- stuck: 120m
