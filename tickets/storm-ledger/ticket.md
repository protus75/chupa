---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-16
- journal-roll

## Context
- chupa/journal.py
- chupa/box.py
- chupa/config.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.storm-ledger
- section 12

## Goal / Why
Direct invocation records and projects stable storm arrivals once across journal rotation and restart while remaining dormant.

## Scope in / Scope out
19.P3.storm-ledger is the complete governing contract for Owner, Records, Observable and every named Tests obligation: implement all of it, including record custody and its sole writers. The renderer injects those bullets verbatim; never copy unit text into this seed. Source module ownership from the unit's Owner, never invent it inline.

Read the merged real CLI run/drain, build_daemon_core and the merged production-composition harness before editing. Preserve bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Do not migrate historical seeding tests. Closure greps across chupa/, eval/ and tests/ under 19.L rules 2-5 earned no fence additions; callable signatures and production composition remain unchanged. Existing fenced paths are Context; created paths (including sibling-created paths) are neither Context nor On-demand. Unfenced tests in the entry-unit Verification are unchanged preservation suites in Verification only, neither fenced nor embedded.

New chupa/storm.py is owned by the occurrence writer and journal-derived projection specified in 19.P3.storm-ledger; Journal remains the sole durable writer. Keep the occurrence-only ledger dormant under the complete entry-unit observable. Out: trip/report/notification/hold, producer or production hook activation, task graphs, manual HGATE release, verification filtering and unearned records.

## Scope fence
- chupa/storm.py
- tests/test_storm.py

## Acceptance criteria
1. `uv run pytest tests/test_storm.py tests/test_journal_roll.py tests/test_journal.py tests/test_box.py` exits 0 proving every boundary, replay, corruption, durability and crash obligation assigned by `19.P3.storm-ledger` through `test_storm_construction_and_reads_are_idle`, `test_occurrence_signal_shape_and_identity`, `test_occurrence_replay_is_once`, `test_window_boundaries_and_signature_isolation`, `test_occurrences_survive_roll_and_restart`, `test_occurrence_append_failures_and_crash_replay`, `test_ledger_has_no_trip_side_effects`, `test_storm_ledger_is_dormant`.
2. `uv run pytest -q` exits 0 with all preservation suites unchanged and public caller behavior retained.

## Verification
```
uv run pytest tests/test_storm.py tests/test_journal_roll.py tests/test_journal.py tests/test_box.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence. Never invent records or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
