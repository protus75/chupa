---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-14

## Context
- chupa/daemon.py
- chupa/__main__.py
- tests/test_daemon_composition.py
- tests/test_daemon_pause.py
- tests/test_control.py
- chupa/reconcile.py
- chupa/journal.py
- chupa/config.py
- chupa/seams.py
- chupa/git.py

## Plan contract
- 19.I
- 19.P3.restart-timers
- section 6
- section 15

## Goal / Why
Make the real daemon composition reconcile and restore durable deadlines before its first dispatch, with explicit idle recovery and injected deadline waits.

## Scope in / Scope out
19.P3.restart-timers is the complete governing contract for Owner, Records, Observable and every named Tests obligation; implement all of it, including record custody. The renderer injects those bullets verbatim. Never copy unit text into this seed. The new chupa/restart.py and chupa/timers.py owners are exactly the unit's Owner. This deep row starts high/high.

Preserve the registry floor and callable signatures. Read runner.harvest_orphan in chupa/runner.py and the real CLI run/drain entry reconciliation in chupa/runner.py and chupa/drain.py before writing. Reuse the merged production-composition harness and real build_daemon_core with barrier-held reconciliation, injected recovery failures and member-local invariant-audited journals, as governed by the entry unit. Preserve bootstrap on-entry reconciliation, inline admission, ordinary DaemonTasks exception propagation and cleanup. serve-activation owns continuous maintenance scheduling; add no serve verb or background loop. Use injected Clock/Sleep and process/filesystem seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits.

Earned predecessor/caller closure under 19.L rules 2-5: tests/test_daemon_composition.py and tests/test_daemon_pause.py pin admission._before_dispatch to the pause checkpoint. Migrate only those identity assertions to prove the composed startup then pause boundary, retaining the pause behavior and calibration. tests/test_control.py:test_control_inbox_is_active and its assert_bound helper pin the same identity; migrate that binding proof and its removal calibration to the composed startup/pause boundary while preserving the active inbox assertion and real CLI control behavior.

Also earn tests/test_daemon_composition.py:test_production_core_preserves_eligibility_order_and_backpressure: its bare running plant precedes the first admission and would become a restart orphan. Await the composed startup before planting running so it remains a live-run eligibility fact, or rewrite the exclusion case to cover the reap. Keep every other eligibility, ordering and backpressure assertion unchanged. The full CoreRig/build_daemon_core caller sweep found tests/test_scheduler.py's leaf-b running plant safe because later terminals close it before dispatch; LiveDrain plants use existing bootstrap recovery or closed terminal history. No other open running or unmatched effect_intent plant precedes a CoreRig first admission.

Keep the existing CLI import line `from chupa.daemon import DaemonCore, PauseConsumer, daemon_core` byte-identical; add new owners on separate import lines to preserve its production-root calibration. No public-operation allowlist forces further paths. All existing fenced paths are Context; created paths are in neither Context nor On-demand. Run unchanged preservation suites in Verification only, neither fenced nor embedded. Never migrate historical seeding tests. Out: replacement recovery/terminal writers or task graphs, altered signatures, recovery_alert, unearned records and consumers outside this entry unit.

## Scope fence
- chupa/restart.py
- chupa/timers.py
- chupa/daemon.py
- chupa/__main__.py
- tests/test_restart_timers.py
- tests/test_daemon_composition.py
- tests/test_daemon_pause.py
- tests/test_control.py

## Acceptance criteria
1. `uv run pytest tests/test_restart_timers.py` exits 0 proving the complete 19.P3.restart-timers contract through `test_restart_construction_is_idle`, `test_restart_reuses_orphan_reconciliation`, `test_orphan_sweep_preserves_live_ownership`, `test_timer_records_and_identity`, `test_timer_append_is_write_ahead`, `test_timers_rearm_from_journal`, `test_timer_deadline_wait_uses_injected_sleep`, `test_production_restart_precedes_dispatch`, `test_restart_failures_do_not_report_ready`.
2. `uv run pytest tests/test_restart_timers.py` proves the entry unit's record custody, sole writers, startup ordering and failure barriers through the named tests and member-local invariant auditor; the full Verification command preserves bootstrap recovery and ordinary admission behavior.
3. `uv run pytest -q` exits 0 with no removed or skipped test, only the earned predecessor migrations, and no new serve verb or continuous loop.

## Verification
```
uv run pytest tests/test_restart_timers.py tests/test_reconcile.py tests/test_daemon_composition.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_cli.py tests/test_drain.py tests/test_journal.py tests/test_audit.py
uv run pytest tests/test_daemon_pause.py tests/test_control.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming 19.P3.restart-timers for section 11.4 hardening if its complete contract omits a needed fact or criteria force an unearned path outside the fence. Never invent records or recovery machinery.

## Time budget
- expected: 60m
- stuck: 90m
