---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase4-continue
- watchdog-detector

## Context
- chupa/watchdog.py
- chupa/driver.py
- chupa/notify.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- tests/test_watchdog.py
- chupa/author.py
- chupa/rework.py
- chupa/triage.py
- eval/diagnose.py
- eval/harness.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_kill_executor_abort.py
- tests/test_kill_failure_suppression.py
- tests/test_llm_effect.py
- tests/test_requisition.py
- chupa/requisition.py
- eval/shakeout/providers.py

## On-demand
- tests/test_daemon_composition.py
- tests/test_serve.py
- chupa/stages.py
- chupa/runner.py
- tests/test_providers.py
- eval/daemon_soak.py

## Plan contract
- 19.I
- 19.P4.watchdog-activation
- section 9
- 19.P4.watchdog-detector
- 19.P4.watchdog-event-stream
- 19.P4.notify-transport

## Goal / Why
Watch every production model call and prove warnings and harvested timeout through production composition.

## Scope in / Scope out
Activate the detector for every production model-call route, including Implement, review, rework, diagnosis, Author, triage and requisition review; future retro calls inherit this watched composition. The cited entry supplies Owner, Records, Observable and Tests. chupa/watchdog.py owns the watched LLM path, chupa/driver.py the run lifetime, chupa/stages.py ticket metadata and chupa/runner.py production binding and harvest custody. Keep Driver constructor/from_config arity, LLMRequest/LLMResult and LLM effect signatures unchanged. Extend the run-call interface to carry expected/stuck budgets and writable scope context; migrate every direct Driver.run caller in the fenced production, eval and test files in this commit. Ticketless calls use their real surface/run sequence and no writable output fence. No compatibility layer or unwatched production route is allowed.

chupa/requisition.py makes a separate llm_call through Driver.race; bind this path to the watched context too, including nested Author/Rework reviews, preserving its effect identity and failure semantics. Keep production serving identity/cost, Implement-only write grants and classification/routing behavior intact. No provider registry or threshold activation belongs here.

Named obligations: test_every_production_driver_surface_is_watched, test_production_soft_band_notifies_once_without_kill, test_production_hard_timeout_group_kill_is_harvested, test_production_watchdog_shares_active_executor. Reuse the real production graph from tests/test_daemon_composition.py and tests/test_serve.py with injected time and adapter events. Exercise every surface, retries, repeated calls and fresh run boundaries. Prove the soft warning's notify intent/completion pair, suppression after retrips/progress and a distinct next-run key, without auto-kill. Prove a hung real child and descendant are group-killed and reaped, the existing timeout result survives, and the existing runner lifts its harvest before deleting the worktree. Tests must not write their own harvest or checks.json evidence.

Transition fixtures: migrate tests/test_watchdog.py::test_event_stream_is_dormant and the sibling detector's test_detector_is_dormant to activated expectations, retaining their discriminating probes and stream/detector assertions. Preserve tests/test_providers.py::test_cli_failure_classifier_is_dormant until provider failover. Preserve merged serve partitioning, existing task/worker counts, and startup/poll notification reconciliation. Revised caller fixtures retain all effect replay, timeout, write-grant, classification, independent kill and failure-suppression assertions. Constructor-only fixtures do not earn fence additions.

Read Context and each On-demand file before editing; read predecessor tickets and grep callers, allowlists and negatives across chupa/, eval/ and tests/. Existing files are partitioned solely by measured headroom; the new tests/test_watchdog_activation.py is never Context. tests/test_notify.py and the other unfenced Verification suites are unchanged preservation obligations. Watched call and abort share the executor that spawned the child; notification and self-upgrade executors remain independent. Retain hold/control behavior, failure-spine ordering, redaction, capture and cleanup. Out: new terminals/signals/reports, provider failover, live-state reads, hand-authored receipts, historical seeding fixtures and ticket/plan edits.

## Scope fence
- chupa/watchdog.py
- chupa/driver.py
- chupa/stages.py
- chupa/notify.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- tests/test_watchdog.py
- tests/test_watchdog_activation.py
- tests/test_daemon_composition.py
- eval/shakeout/providers.py
- eval/daemon_soak.py
- chupa/author.py
- chupa/rework.py
- chupa/triage.py
- eval/diagnose.py
- eval/harness.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_kill_executor_abort.py
- tests/test_kill_failure_suppression.py
- tests/test_llm_effect.py
- tests/test_providers.py
- tests/test_requisition.py
- tests/test_serve.py
- chupa/runner.py
- chupa/requisition.py

## Acceptance criteria
1. `uv run pytest tests/test_watchdog.py tests/test_watchdog_activation.py tests/test_daemon_composition.py tests/test_notify.py` exits 0 proving all four named activation obligations through real production composition, every surface/run context, soft warning once and harvested hard-timeout cleanup.
2. `uv run pytest tests/test_watchdog.py tests/test_watchdog_activation.py tests/test_daemon_composition.py tests/test_notify.py` exits 0 migrating predecessor dormancy fixtures while retaining identity/cost, grants, independent executors, hold/control and stream/detector/transport behavior.
3. `uv run pytest tests/test_driver.py tests/test_echo_stage.py tests/test_kill_executor_abort.py tests/test_kill_failure_suppression.py tests/test_llm_effect.py tests/test_providers.py tests/test_requisition.py tests/test_serve.py` exits 0 retaining revised caller assertions; `uv run pytest tests/test_drain.py tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_seed_path.py tests/test_eval_harness.py tests/test_diagnose_eval.py tests/test_storm_notification_activation.py tests/test_effects.py tests/test_notify.py` exits 0 preserving unfenced suites unchanged.

## Verification
```
uv run pytest tests/test_watchdog.py tests/test_watchdog_activation.py tests/test_daemon_composition.py tests/test_notify.py
uv run pytest tests/test_driver.py tests/test_echo_stage.py tests/test_kill_executor_abort.py tests/test_kill_failure_suppression.py tests/test_llm_effect.py tests/test_providers.py tests/test_requisition.py tests/test_serve.py
uv run pytest tests/test_drain.py tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_seed_path.py tests/test_eval_harness.py tests/test_diagnose_eval.py tests/test_storm_notification_activation.py tests/test_effects.py tests/test_notify.py
uv run pytest tests/test_shakeout.py tests/test_daemon_soak.py tests/test_daemon_soak_runner.py
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. A criteria-forced path outside the earned fence returns premise_failed; repair the contract or closure rather than invent facts or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m

