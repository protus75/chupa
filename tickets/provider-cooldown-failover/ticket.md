---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase4-continue-02

## Context
- chupa/providers.py
- chupa/watchdog.py
- chupa/timers.py
- chupa/restart.py
- chupa/merge.py
- chupa/serve.py
- chupa/__main__.py
- eval/shakeout/bench.py
- chupa/thresh.py
- chupa/driver.py
- chupa/llmeffect.py
- chupa/requisition.py
- eval/shakeout/providers.py
- eval/diagnose.py
- eval/harness.py
- chupa/seams.py
- chupa/effects.py
- chupa/journal.py
- chupa/notify.py
- chupa/audit.py

## On-demand
- eval/daemon_soak.py
- tests/test_daemon_composition.py
- tests/test_serve.py
- chupa/stages.py
- tests/test_mergequeue.py
- chupa/runner.py
- tests/test_providers.py
- tests/test_merge.py
- tests/test_restart_timers.py
- tests/test_stages.py
- chupa/drain.py
- chupa/daemon.py
- tests/test_thresh.py
- tests/test_audit.py
- tests/test_journal.py

## Plan contract
- 19.I
- 19.P4.provider-cooldown-failover
- section 6
- section 15
- 19.P3.thresh-runtime

## Goal / Why
Activate shared provider admission, quota cooldown and subsequent-call failover over the configured candidates. The registry marks this cross-module admission deep, earning high/high under 19.L.

## Scope in / Scope out
Activate the provider admission described by the cited entries. chupa/providers.py owns selection and session cooling state, chupa/thresh.py keeps slot/breaker custody, and chupa/timers.py keeps every durable deadline write. Extend the existing drain/serve production graph and its composition harness. Keep current public Driver.run/from_config, Checkout, build_daemon_core, resolve and LLM request/result signatures; thread the new session state through the existing composition without requiring unrelated caller migrations. Migrate all direct ProviderLLM constructor sites in the fence in one change.

Compose one registry/cooldown payload and one Timers owner for each lock-held drain or serve lifetime, including refreshed config snapshots and ticketless surfaces. Route implement, review, rework, diagnosis, requisition review, triage, Author and future retro through that shared state. Eval roots and scripted benches use the same construction. Select once before the LLM effect and carry that choice through adapter events, watchdog metering, result, completion and harvested run identity. Preserve preflight and snapshot-local config/writer redaction. Clean up owned admission/timer waits with cancellation and awaited completion before releasing the lock.

On a classified quota failure, persist its cooldown using the entry's exact Timer identity and envelope before later routing acts. End and harvest the failed attempt, emit the existing soft report, and avoid an infra draw or inline retry. Exercise a duplicate pending window, a later fresh window, restart before/equal/after expiry, and failed arm/fire appends. Skip unavailable candidates in configured order, retain inherited and pinned models, and preserve the predecessor's FIFO and strict spill boundary. A single-candidate fixture must cool and resume its same identity.

Prove pre-dispatch drought with no running offer or model execution. Journal the entry-defined structured provider_drought transition, project its hold from that field, and release it automatically when routing recovers. A mid-run refusal follows the existing harvest/terminal/cleanup route exactly once, retaining earlier attempt evidence and drawing no cap, diagnosis, escalation ladder or Reject arrival. Cover nested requisition review as well as ordinary stages. Quota holds wait for the earliest relevant Timers deadline; expiry equality and breaker recovery permit fresh selection. Keep normal infra accounting and bounded unknown-failure evidence for executed failures, classifier Finding roads, auth alerts and existing notification/Box custody. Add no event/signal vocabulary or alternate failure spine.

Migrate test_thresh_is_dormant in tests/test_thresh.py and test_cli_failure_classifier_is_dormant in tests/test_providers.py to discriminating activation proofs. Retain the predecessor concurrency, FIFO/reselection, breaker, replay and six-class classifier tests. Preserve merged watchdog event capture, soft warning and group-kill behavior. Admission wait must be excluded from both ticket time and watchdog regions, including cancellation and replay; preserve the sole threshold signal writers and shapes. Read the predecessor tickets thresh-runtime, watchdog-detector and watchdog-activation before editing.

Named obligations in tests/test_provider_cooldown_failover.py: test_quota_failure_arms_cooldown_without_infra_draw, test_ordered_failover_preserves_served_identity, test_all_candidates_cooling_recovers_on_timer_fired, test_mid_run_drought_is_harvested_without_spine_draws, test_single_candidate_cooldown_resumes_same_provider, test_cooldown_reconstructs_and_rearms_new_windows, test_one_provider_payload_and_timers_per_session, test_provider_wait_excluded_from_ticket_and_watchdog_budgets, test_executed_failures_preserve_classification_and_infra_accounting. Each proves all cases assigned by the own entry, through injected seams and a multi-candidate fixture registry. The session test must cover real drain and serve lifetimes, repeated dispatches/config refresh, every ticket-owned and ticketless construction site, and awaited wait cleanup. The wait test must discriminate a queued call from a hung executing call. Extend the real production composition harness rather than creating another graph.

Read every Context and On-demand path before writing. On-demand is the measured headroom partition, including delimiter-bearing eval/daemon_soak.py. Use the existing effect and exception mapping owners in chupa/llmeffect.py and chupa/driver.py; no duplicate effect, classifier, routing or Timer implementation. Keep unfenced Verification suites unchanged as preservation evidence. Out: live provider/config alterations, real-model calls, wall-clock waits, new modules, knobs, signals, terminals, reports, provider dependencies, plan/ticket edits and historical seeding snapshots.

## Scope fence
- chupa/providers.py
- chupa/watchdog.py
- chupa/timers.py
- chupa/runner.py
- chupa/restart.py
- chupa/daemon.py
- chupa/stages.py
- chupa/merge.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- eval/shakeout/bench.py
- eval/daemon_soak.py
- tests/test_provider_cooldown_failover.py
- tests/test_providers.py
- tests/test_restart_timers.py
- tests/test_stages.py
- tests/test_serve.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_daemon_composition.py
- chupa/audit.py
- tests/test_audit.py
- chupa/journal.py
- tests/test_journal.py
- chupa/thresh.py
- tests/test_thresh.py
- chupa/driver.py
- chupa/llmeffect.py
- chupa/requisition.py
- eval/shakeout/providers.py
- eval/diagnose.py
- eval/harness.py

## Acceptance criteria
1. The first `uv run pytest` Verification command exits 0 with all nine named provider obligations, exact cooldown/drought records, identity stamps, bounded failure accounting and predecessor activation proofs.
2. The two targeted `uv run pytest` Verification commands exit 0 preserving production composition, injected wait accounting, preflight, replay, grants, redaction and active-executor abort binding.
3. `uv run pytest -q` exits 0; unchanged preservation suites and historical seeding snapshots remain green.

## Verification
```
uv run pytest tests/test_provider_cooldown_failover.py tests/test_providers.py tests/test_thresh.py tests/test_restart_timers.py tests/test_stages.py tests/test_serve.py tests/test_merge.py tests/test_mergequeue.py tests/test_daemon_composition.py tests/test_watchdog.py tests/test_audit.py tests/test_journal.py
uv run pytest tests/test_driver.py tests/test_drain.py tests/test_watchdog_activation.py tests/test_llm_effect.py tests/test_requisition.py tests/test_notify.py tests/test_shakeout.py tests/test_eval_harness.py tests/test_diagnose_eval.py tests/test_daemon_soak_runner.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. If the criteria require a path outside the earned fence, repair the contract or closure rather than inventing facts or changing the registry.

## Time budget
- expected: 60m
- stuck: 90m
