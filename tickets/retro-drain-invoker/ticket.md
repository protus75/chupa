---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase4-exit

## Context
- chupa/driver.py
- chupa/__main__.py
- chupa/box.py
- tests/test_driver.py
- tests/test_box.py
- chupa/daemon.py
- chupa/journal.py
- tests/test_vocabularies.py
- tests/test_cli.py
- tests/test_drain_upgrade.py
- tests/test_seed_successor.py
- tests/test_daemon_config.py
- tests/test_daemon_admission.py
- tests/test_daemon_pause.py
- tests/test_reconcile.py
- tests/test_flake.py

## On-demand
- chupa/drain.py
- chupa/stages.py
- tests/test_drain.py
- tests/test_stages.py
- chupa/runner.py
- tests/test_storm_hold.py
- tests/test_storm_notification_activation.py

## Plan contract
- 19.I
- 19.P5.retro-drain-invoker
- section 13
- section 14

## Goal / Why
The lock-held bootstrap drain produces retro receipts and immutable declared exit inputs from production evidence.

## Scope in / Scope out
Implement the invoker and journal-window input governed by the cited entry, including all four entry parts. The new module owner is chupa/retro.py; its prompt source is specs/retro.md. Start high/high: the registry marks this row KNOWN-DEEP, crossing window projection, Driver, stages and lock-held drain composition. Reuse the serving session provider payload and existing watched Driver; preserve public call/constructor signatures, adding only the entry-governed public read-only Stages.driver through Pipeline.stages. The current carrier owners are runner.pipeline/PreparedDispatch and daemon.TicketWriter; fence them for that closure. A missing Driver raises RetroConstructionError with the specified paved road, never private ctx traversal or a global driver.

Realize the entry's unforced dispatch checks and forced pre-exit/quiescence calls, awaiting the hook under the existing MAIN lock and re-reading the boundary before selection. Default-off direct drain construction and automatic self-upgrade wiring remain covered. Exercise no-merge no-op and selected failure followed by continued dispatch. Keep report commit/replay and unfinished-intent handling in the existing ticket-plane Git/Effects lane; register only retro_failed in the existing signal vocabulary. Counts, spend, tokens, calibration and provenance come from the real ordered event window, with unknown usage preserved. The model supplies proposals, never fabricated measurements. Leave the scorecard, proposal emission/Box activation and CLI verbs to later admissions.

Resolve Exit-read window declarations using the entry's exact current retro window bound and EVENT_VERSIONS vocabulary. Select the last completed report boundary before filtering the suffix by exact event type; exclude the boundary, include the snapshot's final event, and preserve null-ticket events, order, duplicates and exact envelopes. Use one shared pre-stage snapshot for all declarations, keyed by the canonical declaration rather than the exit stem. Materialize through the Driver filesystem seam. Prove whitespace canonicalization, different exit stems, no-completion, intent-only, multiple boundaries, empty/no-match windows, later-appended events, missing declarations, unsupported types and arbitrary nonblank bounds with their paved road. The consumed exit read works without a live state directory.

Read all Context and On-demand paths before changing them. The authoring snapshot in the merged seeding test records every earned addition and scenario. Migrate only forced fixture/assertion assumptions: public scripted stages carriers for synthetic merged-quiescence fixtures; the upgrade child's commit-offset assertion; the seed-successor exact model-call list and final-main assertion; and the storm test's blanket Effects.run prohibition, narrowing it to notify effects. Script valid retro output through the existing Driver so a missing Driver cannot introduce unrelated failure Box messages into flake absence proofs. Keep dispatch order, lock, retry, pause/resume, kill, park, provider, watchdog, orphan and admission assertions. Shared fixture consumers stay unchanged in preservation Verification. Use no signature or arity changes requiring additional callers outside this closure; any forced path beyond it is premise_failed, not a guessed widening.

Named entry obligations: test_window_uses_completed_report_boundary, test_retro_trigger_boundaries, test_report_commit_replays_without_advancing_unfinished_window, test_failed_retro_suppresses_window_until_completion, test_retro_hook_is_default_off, test_drain_retro_due_quiescence_and_pre_exit, test_retro_driver_access_is_public_and_read_only, test_exit_read_window_materialization. Include test_plan_lint and keep resolver/depth checks green. Use disposable repositories and injected time, filesystem, process and model seams. Out: new scheduling, serve activation, retro/doctor verbs, scorecard, baseline reader, Box proposal activation, live-model calls, journal debug logs, extra reports, plan/ticket edits, historical snapshot migrations and compatibility paths.

## Scope fence
- chupa/retro.py
- specs/retro.md
- tests/test_retro.py
- chupa/drain.py
- chupa/driver.py
- chupa/stages.py
- chupa/__main__.py
- chupa/box.py
- tests/test_drain.py
- tests/test_driver.py
- tests/test_stages.py
- tests/test_box.py
- chupa/runner.py
- chupa/daemon.py
- chupa/journal.py
- tests/test_vocabularies.py
- tests/test_cli.py
- tests/test_drain_upgrade.py
- tests/test_seed_successor.py
- tests/test_daemon_config.py
- tests/test_daemon_admission.py
- tests/test_daemon_pause.py
- tests/test_reconcile.py
- tests/test_flake.py
- tests/test_storm_hold.py
- tests/test_storm_notification_activation.py

## Acceptance criteria
1. `uv run pytest -q tests/test_retro.py tests/test_drain.py tests/test_driver.py tests/test_stages.py tests/test_box.py tests/test_vocabularies.py` exits 0 proving every named entry obligation, production invoker, public access, committed-report replay/failure suppression and declaration-keyed materialization.
2. `uv run pytest -q` exits 0 retaining the recorded scenario migrations and all unchanged preservation suites.
3. `uv run pytest -q tests/test_plan_lint.py` exits 0 with the governing entry resolving once and containing Owner, Records, Observable and Tests.

## Verification
```
uv run pytest -q tests/test_retro.py tests/test_drain.py tests/test_driver.py tests/test_stages.py tests/test_box.py tests/test_vocabularies.py
uv run pytest -q tests/test_vocabularies.py tests/test_cli.py tests/test_drain_upgrade.py tests/test_seed_successor.py tests/test_daemon_config.py tests/test_daemon_admission.py tests/test_daemon_pause.py tests/test_reconcile.py tests/test_flake.py tests/test_storm_hold.py tests/test_storm_notification_activation.py
uv run pytest -q tests/test_drain_reentry.py tests/test_ladder.py tests/test_diagnose.py tests/test_harvest.py tests/test_audit.py tests/test_merge.py tests/test_storm_producer.py tests/test_daemon_composition.py tests/test_provider_cooldown_failover.py tests/test_watchdog_activation.py tests/test_restart_timers.py tests/test_kill_cli_activation.py tests/test_kill_executor_abort.py tests/test_kill_signal_journal.py tests/test_seed_path.py tests/test_reject_queue.py tests/test_caps.py tests/test_control_cli.py tests/test_daemon_tasks.py tests/test_heartbeat.py tests/test_checkpoint.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A missing governing fact is premise_failed, kind: spec_gap, naming its owning cited unit. A criteria-forced path outside the earned fence requires contract repair; never widen speculatively or fabricate evidence.

## Time budget
- expected: 60m
- stuck: 180m
