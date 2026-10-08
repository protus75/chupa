---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-20

## Context
- chupa/daemon.py
- chupa/__main__.py
- tests/test_daemon_tasks.py
- tests/test_kill_worker_stop.py
- tests/test_kill_failure_suppression.py
- tests/test_heartbeat.py
- tests/test_storm.py
- tests/test_restart_timers.py
- tests/test_checkpoint.py
- chupa/runner.py
- chupa/merge.py
- chupa/triage.py
- chupa/checkpoint.py
- chupa/control.py
- chupa/scheduler.py
- chupa/watcher.py
- chupa/restart.py
- chupa/timers.py

## On-demand
- tests/test_daemon_composition.py
- chupa/driver.py

## Plan contract
- 19.I
- 19.P3.serve-activation
- section 18
- section 20

## Goal / Why
Activate the continuous foreground production serve lifetime governed by 19.P3.serve-activation.

## Scope in / Scope out
19.P3.serve-activation is the complete governing contract: implement its entire Owner, Records, Observable and Tests obligations, including every named invariant, record custody and sole writer. The renderer injects those bullets verbatim; never copy unit text into this seed. chupa/serve.py is owned by its cited Owner. Start high/high because the live registry row is deep under 19.L. Preserve the registry fence floor; no row splitting or historical seeding snapshot migration.

The two earned additions under 19.L rules 2-3 are tests/test_restart_timers.py for test_restart_construction_is_idle's CLI serve-absence assertion (migrate only that assertion, preserving startup/timer invariants), and tests/test_checkpoint.py for test_checkpoint_boundary_is_dormant's production activation assertion (preserve checkpoint invariants and run/drain dormancy). Both are existing paths in Context. tests/test_storm.py remains the registry floor's existing Context path; retain test_storm_ledger_is_reachable as positive evidence.

Use the real CLI/async serve entrypoint and merged production-composition harness. Read the On-demand harness before writing; its measured embedding breaches 300,000-character headroom. Existing fenced paths otherwise remain Context. Read merged chupa/stages.py, chupa/mergequeue.py, chupa/git.py, chupa/journal.py, chupa/effects.py, chupa/box.py, chupa/storm.py, chupa/config.py, chupa/drain.py and chupa/seams.py as further read-only seam references before touching their callers. Keep existing composition callers valid without a second production path or changed public signatures. Re-grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/ before any criteria-forced closure claim. No additional production owner is earned by the authoring-head greps.

Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer, as governed by the cited Records contract. No caller-read records, replacement writers, notify transport or daemon-admission routing are earned here; serve-merge-admission owns later routing activation. All activation evidence uses injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers; no test-only graph, live host work, real-model calls or wall-clock waits.

Unfenced Verification suites stay unchanged preservation suites, neither fenced nor embedded. Prompt-specs and delimiter-bearing sources are never Context. Out: plan/registry edits, historical tests, new records or config, later payload implementation and manual HGATE release.

## Scope fence
- chupa/serve.py
- chupa/daemon.py
- chupa/__main__.py
- chupa/triage.py
- chupa/driver.py
- tests/test_serve.py
- tests/test_daemon_composition.py
- tests/test_daemon_tasks.py
- tests/test_kill_worker_stop.py
- tests/test_kill_failure_suppression.py
- tests/test_heartbeat.py
- tests/test_storm.py
- tests/test_restart_timers.py
- tests/test_checkpoint.py

## Acceptance criteria
1. `uv run pytest tests/test_serve.py tests/test_daemon_composition.py tests/test_daemon_tasks.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_heartbeat.py tests/test_storm.py tests/test_checkpoint.py tests/test_restart_timers.py tests/test_control.py tests/test_control_cli.py tests/test_kill_cli_activation.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py tests/test_audit.py` exits 0 proving the full cited 19.P3.serve-activation Owner/Records/Observable/Tests contract, with these named obligations: `test_serve_cli_uses_production_composition`, `test_serve_holds_lock_through_cleanup`, `test_serve_startup_precedes_all_work`, `test_serve_waits_at_quiescence_and_discovers_work`, `test_serve_consumers_use_existing_writers`, `test_serve_control_precedes_offer_accounting`, `test_serve_kill_unwinds_executor_before_workers`, `test_serve_worker_failure_and_kill_suppression`, `test_serve_signal_stop_and_restart_recovery`, `test_serve_recurring_maintenance_uses_injected_time`, `test_serve_heartbeat_requires_responsive_components`, `test_serve_storm_hold_and_resume`, `test_production_serve_graph_is_reachable`.
2. The same `uv run pytest tests/test_serve.py tests/test_daemon_composition.py tests/test_daemon_tasks.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_heartbeat.py tests/test_storm.py tests/test_checkpoint.py tests/test_restart_timers.py tests/test_control.py tests/test_control_cli.py tests/test_kill_cli_activation.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py tests/test_audit.py` exits 0 after the governing predecessor migrations, including `test_background_consumers_are_dormant`, `test_kill_worker_stop_is_dormant`, `test_kill_failure_suppression_is_dormant`, `test_heartbeat_is_dormant`, `test_checkpoint_boundary_is_dormant`, `test_restart_construction_is_idle` and positive `test_storm_ledger_is_reachable`; run/drain and component invariants remain green.
3. `uv run pytest tests/test_serve.py tests/test_daemon_composition.py tests/test_daemon_tasks.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_heartbeat.py tests/test_storm.py tests/test_checkpoint.py tests/test_restart_timers.py tests/test_control.py tests/test_control_cli.py tests/test_kill_cli_activation.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py tests/test_audit.py` exits 0 with every named invariant and record custody proved through the exact governing citations, using the production graph and existing writers; preservation suites remain unchanged.

## Verification
```
uv run pytest tests/test_serve.py tests/test_daemon_composition.py tests/test_daemon_tasks.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_heartbeat.py tests/test_storm.py tests/test_checkpoint.py tests/test_restart_timers.py tests/test_control.py tests/test_control_cli.py tests/test_kill_cli_activation.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py tests/test_audit.py
```

## Definition of rejected
Return premise_failed naming a missing or contradictory fact in 19.P3.serve-activation for section 11.4 hardening, or a criteria-forced file outside the earned fence; never invent records or widen scope. A fact the entry unit omits or contradicts is reported as a `spec_gap` finding naming its unit (section 11.4), never invented.

## Time budget
- expected: 60m
- stuck: 180m
