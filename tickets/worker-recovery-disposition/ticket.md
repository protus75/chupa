---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-22

## Context
- chupa/reconcile.py
- tests/test_reconcile.py
- chupa/journal.py
- tests/test_restart_timers.py
- tests/test_kill_failure_suppression.py

## Plan contract
- 19.I
- 19.P3.worker-recovery-disposition
- section 6
- section 15

## Goal / Why
Record the producing orphan run's recovery disposition at the existing reap boundary.

## Scope in / Scope out
Implement the cited recovery entry in place. Its Owner, Records, Observable and Tests parts govern the exact evidence, custody, ordering, failure behavior and invariant obligations; cite them rather than duplicating their bodies. The registry marks this row deep, earning high/high at birth.

The registry floor is chupa/reconcile.py and tests/test_reconcile.py. The recovery entry earns chupa/journal.py for SIGNAL_NAMES registration at the Journal seam and tests/test_restart_timers.py for the removal assertion in test_restart_reuses_orphan_reconciliation. Authoring-time grep additionally earns tests/test_kill_failure_suppression.py under contradicted-test closure: test_kill_suppression_preserves_run_and_abort_failures asserts that abandonment is reconciliation's final record. Migrate only the assertions invalidated by ordered recovery evidence, preserving each predecessor's other guarantees.

Named obligations, all governed by 19.P3.worker-recovery-disposition:
- test_recovery_alert_records_producing_run
- test_recovery_alert_precedes_worktree_removal
- test_recovery_alert_is_once_per_reaped_run
- test_recovery_alert_failures_preserve_terminal_history
- test_recovery_alert_does_not_change_disposition
- test_every_engine_signal_name_is_listed
- test_listed_signal_names_are_accepted
- test_unknown_signal_name_is_refused_at_append
- test_restart_reuses_orphan_reconciliation

That unit also governs clean/empty and historical non-ok no-ops, intent-only evidence, missing worktrees, later re-entry, shared startup/sweep ownership, live-run exclusion, and the existing auditor's missing-running-witness result. Keep vocabulary preservation tests unchanged. The producing sequence is captured before abandonment; ordered recovery evidence, failure ordering, idempotence and unchanged disposition are judged through the cited entry's named tests. Migrate test_kill_suppression_preserves_run_and_abort_failures to that same evidence contract.

Record custody remains with the cited owners: reconcile.py supplies RECOVERY_ALERT and recovery/abandonment emission; Journal alone durably appends events and owns run_seq, TERMINAL_STATES, envelope and SIGNAL_NAMES. Box alone writes queue records; ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close and reconciliation caller signatures, bootstrap on-entry recovery, Restart startup/idle ownership and ordinary DaemonTasks exception propagation and cleanup. No notification transport or routing work belongs here.

Read current direct callers and production roots before implementation, including runner, drain, Restart, Timers, CLI run/drain and build_daemon_core, serve and the merged production-composition harness. Production evidence uses the real CLI/async serve entrypoint and merged harness when applicable, with injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers. Never use a test-only graph, live host work, real-model calls or wall-clock waits. No second recovery implementation, new records or replay subsystem is earned. Unfenced suites in Verification are unchanged preservation suites.

## Scope fence
- chupa/reconcile.py
- tests/test_reconcile.py
- chupa/journal.py
- tests/test_restart_timers.py
- tests/test_kill_failure_suppression.py

## Acceptance criteria
1. `uv run pytest tests/test_reconcile.py tests/test_restart_timers.py tests/test_cli.py tests/test_drain.py tests/test_journal.py tests/test_vocabularies.py tests/test_audit.py` exits 0 and proves the cited unit's named producing-run, ordered removal, repeat-run, failure-history and disposition obligations, including the real Journal vocabulary round trip.
2. `uv run pytest tests/test_kill_failure_suppression.py` exits 0 after migrating its contradictory last-record assertion; the required restart assertion follows the same cited recovery ordering.
3. `uv run pytest tests/test_reconcile.py tests/test_restart_timers.py tests/test_cli.py tests/test_drain.py tests/test_journal.py tests/test_vocabularies.py tests/test_audit.py` exits 0 with unchanged vocabulary preservation suites, public signatures, shared recovery ownership and the cited record custody.

## Verification
```
uv run pytest tests/test_reconcile.py tests/test_restart_timers.py tests/test_cli.py tests/test_drain.py tests/test_journal.py tests/test_vocabularies.py tests/test_audit.py
uv run pytest tests/test_kill_failure_suppression.py
```

## Definition of rejected
Stop with premise_failed naming the governing entry when a needed fact is absent or contradicts merged code, or a forced edit lies outside the earned fence. Never invent a recovery record or custody rule.

## Time budget
- expected: 60m
- stuck: 90m
