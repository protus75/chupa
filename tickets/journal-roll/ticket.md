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

## Context
- chupa/journal.py
- chupa/box.py
- chupa/config.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.journal-roll
- section 6

## Goal / Why
Journal append synchronously rotates at the engine size or age boundary while preserving durable ordered history and existing callers.

## Scope in / Scope out
19.P3.journal-roll is the complete governing contract for Owner, Records, Observable and every named Tests obligation: implement all of it, including record custody and its sole writer. The renderer injects those bullets verbatim; never copy unit text into this seed. Source ownership from the unit's Owner.

Read merged real CLI run/drain, build_daemon_core and the merged production-composition harness before editing. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Preserve all entry-unit boundary, replay, corruption, durability and crash obligations. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Do not migrate historical seeding tests.

Closure greps across chupa/, eval/ and tests/ under 19.L rules 2-5 earned no fence additions. In tests/test_journal.py::test_append_goes_to_newest_segment_without_rolling the event timestamps equal the injected clock despite older segment filenames; the age rule preserves that assertion. Existing fenced paths are Context; created paths are neither Context nor On-demand. Unfenced tests in the entry-unit Verification are unchanged preservation suites in Verification only, neither fenced nor embedded. Journal remains the sole durable writer. Out: replacement writers, tasks, config knobs, live-short-write repair, storm implementation or activation, manual HGATE release, verification filtering and unearned records.

## Scope fence
- chupa/journal.py
- tests/test_journal_roll.py

## Acceptance criteria
1. `uv run pytest tests/test_journal_roll.py tests/test_journal.py tests/test_effects.py tests/test_audit.py` exits 0 proving the complete `19.P3.journal-roll` contract through `test_roll_constants_and_size_boundary`, `test_roll_age_boundary_uses_injected_clock`, `test_roll_sequence_and_restart`, `test_roll_preserves_records_and_read_laws`, `test_startup_tail_repair_precedes_roll`, `test_roll_durability_and_failures`.
2. `uv run pytest -q` exits 0 with unchanged preservation suites and public caller behavior retained.

## Verification
```
uv run pytest tests/test_journal_roll.py tests/test_journal.py tests/test_effects.py tests/test_audit.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence. Never invent records or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
