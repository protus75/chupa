---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-04

## Context
- chupa/runner.py
- chupa/__main__.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.dispatch-admission-boundary
- section 9

## Goal / Why
Build a dormant single-flight dispatch boundary that owns and fully unwinds its callback task before admitting another ticket.

## Scope in / Scope out
- **Owner:** `chupa/daemon.py` owns `DaemonAdmission`, the dormant single-flight boundary around an injected `chupa.runner.Dispatch`. Its async `dispatch(ticket)` operation accepts the selected `Ticket`, owns the task executing that callback, and awaits its completion. `chupa/scheduler.py` retains eligibility, priority/age ordering, pending-ticket removal, and completed-but-unmerged backpressure; this boundary does not select tickets. Existing runner, stage, and merge owners retain pipeline execution, failure handling, durable accounting, and merge admission. Construction changes only `chupa/daemon.py` and `tests/test_daemon_admission.py`; production composition is deferred to `scheduler-activation`.
- **Records:** The input is the existing parsed `Ticket`, passed unchanged to the injected `Dispatch` (`Callable[[Ticket], Awaitable[str]]`). The callback's terminal string is returned unchanged; exceptions and cancellation propagate to the caller. The boundary's `active` ticket and `task` (`asyncio.Task[str]`) are memory-only ownership references, both `None` when idle. Acquire one serial slot before creating the task and retain it until the callback has fully unwound; publish both references for the active dispatch and clear both before releasing the slot. Waiting callers own no callback task. No new journal event, signal, body key, frontmatter value, artifact, config key, or engine constant is introduced. Existing `running` transitions and retry-cap draws remain with their dispatch-accounting writers in `chupa/runner.py` and `chupa/drain.py`; non-ok terminals remain runner-owned, and merged terminals remain merge-owned. This wrapper writes none of them and does not retry, translate a failure into a terminal, or duplicate admission accounting.
- **Observable:** Direct component tests exercise real `DaemonAdmission` with an injected async dispatch callback. Concurrent calls cannot overlap callbacks; a waiting request neither interrupts nor replaces the active ticket. Construction creates no task until explicitly dispatched. Each admitted call invokes the callback exactly once and returns its result only after completion. Success, exception, and cancellation all finish callback cleanup, clear ownership references, and release the slot so a subsequent dispatch can proceed. Cancelling a waiting caller never invokes its callback or disturbs the active task; cancelling the active dispatch cancels and awaits its owned callback before another dispatch starts. No detached worker survives the dispatch that owns it.

  Dormancy is behavioral under `19.I`: production CLI `run` and `drain` continue using their existing pipeline callback without constructing or calling this boundary. Before the production-composition harness exists, test the real CLI composition root with the existing injectable pipeline seam and a raising probe on `DaemonAdmission.dispatch`; the probe must fail the test if the new seam is wired. Also pin the absence of `chupa.daemon` from the transitive CLI import closure, recognizing both import idioms. `scheduler-activation` fences and migrates these assertions when it wires the boundary. Config snapshots, background-consumer ownership, pause, kill, daemon merge routing, and the continuous `serve` loop belong to their later registry rows.
- **Tests:** `tests/test_daemon_admission.py` names `test_admission_is_idle_until_dispatch` (no callback or task at construction, idle references); `test_dispatch_owns_task_and_returns_terminal` (same ticket, exactly one callback, observable active task, unchanged terminal and cleared references); `test_concurrent_dispatch_is_single_flight` (blocked first callback, waiting second call, no overlap or preemption); `test_dispatch_exception_unwinds_and_releases_slot` (original exception propagates, cleanup completes, next dispatch succeeds); `test_cancelled_waiter_never_dispatches` (active task unaffected, no callback for the cancelled waiter); `test_active_cancellation_awaits_cleanup_before_release` (callback cleanup held behind an injected barrier, no second callback until cleanup completes, cancellation propagates, no live owned task); and `test_daemon_admission_is_dormant` (real CLI `run` and `drain` composition with the raising probe, plus the `19.I` transitive import-closure scan proven to fail when reachable). Synchronize with injected callbacks and asyncio barriers, never wall-clock sleeps or real-model calls. Verification runs `uv run pytest tests/test_daemon_admission.py tests/test_scheduler.py tests/test_cli.py tests/test_drain.py`; the last three are unchanged preservation suites. No existing public signature or production caller changes during construction.

Out: activation, public signature or constructor changes, production caller changes, and all later registry machinery. Keep every preservation suite unchanged, Verification-only, neither fenced nor embedded.

## Scope fence
- chupa/daemon.py
- tests/test_daemon_admission.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_admission.py tests/test_scheduler.py tests/test_cli.py tests/test_drain.py` exits 0, exercising every Owner, Records, Observable and named Tests obligation stated above through the real dormant components and injected seams.
2. `uv run pytest -q` exits 0 with no existing test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest tests/test_daemon_admission.py tests/test_scheduler.py tests/test_cli.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject if the new seam is called in production, daemon enters the CLI import closure during construction, task cleanup is incomplete, a waiter disturbs active work, accounting is duplicated, or meeting a criterion requires an out-of-fence edit; return premise_failed naming any missing governing fact instead of inventing it.

## Time budget
- expected: 60m
- stuck: 90m
