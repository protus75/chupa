---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-17
- storm-producer-wiring

## Context
- chupa/storm.py
- chupa/box.py
- chupa/daemon.py
- chupa/__main__.py
- tests/test_storm.py
- tests/test_drain.py
- chupa/runner.py
- chupa/stages.py
- chupa/flake.py
- chupa/journal.py
- chupa/config.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.storm-notification-activation
- section 12

## Goal / Why
Production arrivals reach the storm ledger and threshold evaluator, yielding one trip and P0 report without dispatch suppression or external notification.

## Scope in / Scope out
19.P3.storm-notification-activation is the complete governing contract for Owner, Records, Observable and every named Tests obligation: implement all of it, including record custody and its sole writers. The renderer injects those bullets verbatim; never copy unit text into this seed. Source ownership from the unit's Owner.

Read merged chupa/journal.py, chupa/box.py, chupa/config.py, chupa/daemon.py, chupa/runner.py, chupa/stages.py and chupa/flake.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before editing. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer and Box the sole queue-record writer. Preserve occurrence, replay, window, corruption, durability and crash obligations. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits.

The registry fence is a floor. Authoring-time greps of Box constructors/enqueue, Journal callers, public surfaces, build_daemon_core and production absence assertions across chupa/, eval/ and tests/ earned only the closure described below under 19.L rules 2-5. Optional keyword-only seams preserve callback-free direct callers; no public-operation allowlist or constructor-arity migration is earned. Existing fenced paths are Context; created paths, including sibling-created paths, are neither Context nor On-demand. Unfenced suites are unchanged preservation suites in Verification only, neither fenced nor embedded. Do not migrate historical seeding tests. Out: replacement writers, task graphs, manual HGATE release, verification filtering and unearned records.

Earned additions: chupa/runner.py, chupa/stages.py and chupa/flake.py under 19.L rule 5 for the arrival callers/seam assigned by the governing Owner and Records; all three are Context. tests/test_storm_producer.py is earned under 19.L rules 2-3 for its predecessor production-absence assertion; it is created by this admission's sibling, so never Context here or On-demand. Migrate only the predecessor import/no-trip and production-absence assertions required by the complete unit, preserving occurrence and producer identity/count obligations. The governing Records owns the closed production arrival-site list and all replay-stable occurrence_id recipes; never derive new records from caller reads. Prove these with test_production_arrival_site_closure, test_production_occurrence_id_recipes and test_production_arrival_preserves_caller_behavior.

tests/test_drain.py::test_drain_merges_without_scanning_the_box currently has triage-call and pending-status assertions, not a blanket no-box-event assertion: preserve its non-consumption proof; migrate only a blanket absence assertion if present. Activation invokes no external notify transport or dispatch suppression. storm-dispatch-hold alone owns the later hold and identity-bound release; test_storm_activation_does_not_hold_dispatch_or_notify proves this boundary.

## Scope fence
- chupa/storm.py
- chupa/box.py
- chupa/daemon.py
- chupa/__main__.py
- tests/test_storm.py
- tests/test_drain.py
- tests/test_storm_notification_activation.py
- chupa/runner.py
- chupa/stages.py
- chupa/flake.py
- tests/test_storm_producer.py

## Acceptance criteria
1. `uv run pytest tests/test_storm_notification_activation.py tests/test_storm.py tests/test_storm_producer.py tests/test_drain.py tests/test_box.py tests/test_journal.py tests/test_journal_roll.py` exits 0 proving the complete `19.P3.storm-notification-activation` contract through `test_production_occurrence_id_recipes`, `test_production_arrival_preserves_caller_behavior`, `test_production_arrivals_and_dedup_hits_trip_once`, `test_storm_threshold_window_and_signature_isolation`, `test_storm_trip_targets_are_closed`, `test_storm_trip_and_report_crash_replay`, `test_storm_trip_evidence_fails_closed`, `test_storm_report_cannot_recurse`, `test_storm_activation_does_not_hold_dispatch_or_notify`, `test_production_arrival_site_closure`, `test_drain_merges_without_scanning_the_box`.
2. `uv run pytest -q` exits 0 with no tests removed or skipped and preservation suites unchanged.

## Verification
```
uv run pytest tests/test_storm_notification_activation.py tests/test_storm.py tests/test_storm_producer.py tests/test_drain.py tests/test_box.py tests/test_journal.py tests/test_journal_roll.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence; never invent records or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
