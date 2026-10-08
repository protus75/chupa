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

## Context
- chupa/storm.py
- chupa/box.py
- chupa/daemon.py
- tests/test_storm.py
- chupa/journal.py
- chupa/config.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.storm-producer-wiring
- section 12

## Goal / Why
Direct invocation of the dormant Box arrival hook records stable occurrences, including dedup hits, while production behavior stays unchanged.

## Scope in / Scope out
19.P3.storm-producer-wiring is the complete governing contract for Owner, Records, Observable and every named Tests obligation: implement all of it, including record custody and its sole writers. The renderer injects those bullets verbatim; never copy unit text into this seed. Source ownership from the unit's Owner.

Read merged chupa/journal.py, chupa/box.py, chupa/config.py, chupa/daemon.py, chupa/runner.py, chupa/stages.py and chupa/flake.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before editing. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer and Box the sole queue-record writer. Preserve occurrence, replay, window, corruption, durability and crash obligations. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits.

The registry fence is a floor. Authoring-time greps of Box constructors/enqueue, Journal callers, public surfaces, build_daemon_core and production absence assertions across chupa/, eval/ and tests/ earned only the closure described below under 19.L rules 2-5. Optional keyword-only seams preserve callback-free direct callers; no public-operation allowlist or constructor-arity migration is earned. Existing fenced paths are Context; created paths, including sibling-created paths, are neither Context nor On-demand. Unfenced suites are unchanged preservation suites in Verification only, neither fenced nor embedded. Do not migrate historical seeding tests. Out: replacement writers, task graphs, manual HGATE release, verification filtering and unearned records.

No fence additions are earned. Migrate only tests/test_storm.py::test_storm_ledger_is_dormant's import-absence assertion if importing the hook makes storm reachable; the governing behavioral proof belongs to test_storm_producer_hook_is_dormant. Preserve test_ledger_has_no_trip_side_effects and all predecessor occurrence obligations. Producer wiring stays behaviorally dormant until storm-notification-activation. Out: production caller changes, trip/report/notification/dispatch hold or release.

## Scope fence
- chupa/storm.py
- chupa/box.py
- chupa/daemon.py
- tests/test_storm.py
- tests/test_storm_producer.py

## Acceptance criteria
1. `uv run pytest tests/test_storm_producer.py tests/test_storm.py tests/test_box.py tests/test_daemon_composition.py tests/test_journal.py tests/test_journal_roll.py` exits 0 proving the complete `19.P3.storm-producer-wiring` contract through `test_new_and_dedup_arrivals_record_occurrences`, `test_arrival_replay_survives_restart_and_roll`, `test_dedup_preserves_resolved_message_and_incoming_identity`, `test_invalid_arrivals_and_callback_failures_do_not_publish`, `test_enqueue_crash_replay_finishes_once`, `test_box_operations_without_arrivals_are_idle`, `test_storm_producer_hook_is_dormant`.
2. `uv run pytest -q` exits 0 with no tests removed or skipped and preservation suites unchanged.

## Verification
```
uv run pytest tests/test_storm_producer.py tests/test_storm.py tests/test_box.py tests/test_daemon_composition.py tests/test_journal.py tests/test_journal_roll.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence; never invent records or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
