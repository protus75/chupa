---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-18

## Context
- chupa/storm.py
- chupa/control.py
- chupa/daemon.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_storm_notification_activation.py
- tests/test_storm.py
- tests/test_storm_producer.py
- chupa/journal.py
- chupa/box.py
- chupa/config.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.storm-dispatch-hold
- section 12
- section 20

## Goal / Why
Activate the identity-bound storm dispatch hold and resume in the live bootstrap drain, while unrelated eligible work continues.

## Scope in / Scope out
19.P3.storm-dispatch-hold is the complete governing contract for Owner, Records, Observable and every named Tests obligation: implement all of it. Its Records governs record custody and release authority; its Owner assigns every seam. The renderer injects those bullets verbatim; never copy unit text or derive new records from caller reads. The registry row is deep, so start high/high under 19.L. Preserve its registry floor.

Earned closure under 19.L rules 2-5 adds tests/test_storm_notification_activation.py (rules 2-3: predecessor dispatch-absence test_storm_activation_does_not_hold_dispatch_or_notify and test_storm_leaves_daemon_selection_and_accounting_unchanged), tests/test_storm.py (rules 2-3: test_ledger_trip_uses_only_journal_and_box's hold prohibition), and tests/test_storm_producer.py (rules 2-3: test_storm_producer_hook_is_active's hold prohibition). All three additions are existing Context. Migrate only assertions the hold activation invalidates to positive hold/release evidence and retain the no-external-notify proof, direct construction idleness, and occurrence, replay, window, corruption, durability and crash obligations. The explicit run path stays operator-invoked; continuous serve stage selection remains section 12's later composition contract. Do not migrate historical seeding tests.

Before changing wiring, grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Keep existing public signatures where no change is required; a criteria-forced path not earned in this fence returns premise_failed. Read merged chupa/journal.py, chupa/box.py, chupa/config.py, chupa/storm.py, chupa/control.py, chupa/daemon.py, chupa/drain.py, chupa/runner.py, chupa/stages.py, chupa/flake.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before editing. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer.

Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Unfenced suites are unchanged preservation suites in Verification only, neither fenced nor embedded. Out: replacement writers, second inbox, task graphs, manual HGATE release, notification transport, verification filtering, unearned records and adjacent cleanup.

## Scope fence
- chupa/storm.py
- chupa/control.py
- chupa/daemon.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_storm_hold.py
- tests/test_storm_notification_activation.py
- tests/test_storm.py
- tests/test_storm_producer.py

## Acceptance criteria
1. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_live_drain_holds_only_emitting_stem` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
2. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_storm_hold_precedes_all_dispatch_accounting` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
3. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_non_pipeline_and_non_ticket_trips_do_not_hold` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
4. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_live_resume_releases_in_same_drain` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
5. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_storm_resume_is_identity_bound_and_once` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
6. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_multiple_storm_holds_release_independently` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
7. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_storm_hold_survives_restart_roll_and_expiry` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
8. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_storm_release_rearms_on_new_arrivals_only` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
9. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_storm_hold_crash_and_corrupt_evidence` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
10. `uv run pytest tests/test_storm_hold.py` exits 0 with `test_storm_wait_preserves_kill_budget_and_quiescence` proving its complete invariant obligation under 19.P3.storm-dispatch-hold; governing Records supplies custody and authority.
11. `uv run pytest tests/test_storm_hold.py` exits 0 after the earned predecessor migrations, preserving no-external-notify and all unchanged preservation suites.
12. `uv run pytest -q` exits 0 with no removed or skipped test and no unrelated production behavior changed.

## Verification
```
uv run pytest tests/test_storm_hold.py tests/test_storm_notification_activation.py tests/test_storm.py tests/test_storm_producer.py tests/test_control.py tests/test_control_cli.py tests/test_daemon_pause.py tests/test_drain.py tests/test_kill_cli_activation.py tests/test_daemon_composition.py tests/test_box.py tests/test_journal.py tests/test_journal_roll.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path not earned within the fence. Never invent records or widen scope.

## Time budget
- expected: 90m
- stuck: 180m
