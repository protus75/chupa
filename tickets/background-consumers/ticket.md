---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-07

## Context
- chupa/daemon.py
- chupa/watcher.py
- chupa/mergequeue.py
- chupa/triage.py

## Plan contract
- 19.I
- 19.P3.background-consumers

## Goal / Why
Owned watcher, merge-queue, and box-consumer tasks (DaemonTasks).

## Scope in / Scope out
- **Owner:** `chupa/daemon.py` owns `DaemonTasks`, the lifetime boundary for the watcher, merge-queue, and Suggestion Box consumer tasks. No new engine module is introduced. Supply three named zero-argument async callbacks (`watcher`, `merge_queue`, `box_consumer`) at construction and explicitly await `run()` to drive them. Existing `Watcher.run(changes)` owns change consumption, debounce tasks, parsing, and watcher cleanup; `MergeQueue.process()` owns serial admission and its results; `triage_pass(checkout, llm)` owns sequential box triage and Author routing. Inject callbacks around those existing operations, never copy their algorithms or change their signatures. Construction changes only `chupa/daemon.py` and the new `tests/test_daemon_tasks.py`; production task startup and continuous consumer loops belong to `serve-activation`.
- **Records:** The three callbacks return awaitables; their return values are not dispatch terminals or merge results to reinterpret. `DaemonTasks` owns one task per callback during an explicit run and exposes those ownership references as a memory-only `tasks` tuple, empty before startup and after complete cleanup. Create callbacks' awaitables inside the owned tasks, so construction invokes nothing and a synchronous callback failure follows the same cleanup path as an async failure. Invoke each callback exactly once per run; never restart a failed consumer automatically. Refuse an overlapping run before invoking any callback, with the paved road to finish or cancel and await the existing run first. A later explicit run may begin only after all previous tasks have unwound.

  Existing watcher, queue, triage, Author, intake, runner, and merge writers retain their records and decisions. The task owner reads no ticket frontmatter, config field, journal event, or artifact and writes none. It adds no signal, body key, event type, frontmatter value, config key, engine constant, durable task registry, retry counter, or failure-report writer. A consumer's exception or cancellation is propagated to the awaiting caller, never converted into success, a run terminal, a retry, or a box message. The owner does not discard or manufacture queue outcomes: handling results from `MergeQueue.process()` remains the supplied consumer's responsibility.
- **Observable:** An explicit run starts all three consumers concurrently and remains their lifetime owner. Normal completion awaits all three; one consumer finishing does not cancel the others. A consumer failure cancels the remaining consumers and awaits every task's cleanup before propagating failure. Cancelling the owning run likewise cancels and awaits every consumer before clearing references or allowing a subsequent run. Repeated cancellation during cleanup cannot detach a consumer or let another run overlap that cleanup. Watcher cleanup includes its outstanding debounce tasks through the existing `Watcher.run` unwind; merge admission cleanup remains queue-owned. No task exception is left unobserved and no owned task survives the run. Use asyncio synchronization and injected consumer callbacks; timing and external effects remain behind their existing seams. No polling interval, filesystem watcher dependency, task restart policy, or additional loop is introduced here.

  Construction is dormant under `19.I`: production graph construction and CLI `run`/`drain` neither construct nor run `DaemonTasks`, and bootstrap box consumption remains operator-driven. Test the existing production composition harness once available; before that harness exists, use the real CLI composition root and its injectable pipeline seam. A raising construction/run probe must discriminate deliberate test wiring from the unchanged production path. Do not require `chupa.daemon` to be absent from the import closure: scheduler activation makes that module reachable before this row. `serve-activation` fences `tests/test_daemon_tasks.py` and migrates this behavioral dormancy assertion when it starts the owned consumers.
- **Tests:** `tests/test_daemon_tasks.py` names `test_construction_is_idle` (no callback, awaitable, or task, empty ownership tuple); `test_run_owns_three_concurrent_consumers` (all three enter before barriers release, exactly one invocation each, normal completion waits for every consumer, cleared references); `test_consumer_failure_cancels_and_awaits_siblings` (synchronous and async failures, blocked sibling cleanup, failure propagation only after unwind, exceptions observed); `test_run_cancellation_awaits_all_cleanup` (active consumers cancelled, repeated owner cancellation, no live task or premature reference clearing); `test_watcher_debounce_tasks_do_not_outlive_owner` (real injected `Watcher.run`, outstanding debounce waits cancelled and awaited); `test_overlapping_run_is_refused_until_cleanup_finishes` (no duplicate callbacks, paved refusal, success/failure/cancellation followed by a clean explicit run); `test_merge_results_remain_consumer_owned` (the supplied callback receives and handles queue results without owner interpretation); and `test_background_consumers_are_dormant` (production harness or real CLI `run`/`drain`, no background startup or box triage, probes proven to fail under deliberate wiring). Verification runs `uv run pytest tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py` once the predecessor composition harness has merged; all except the new task test file are unchanged preservation suites. Use injected seams, scripted callbacks, and asyncio barriers, never real-model calls or wall-clock waits.

CONSTRUCTION BOUNDARY: Preserve bootstrap run/drain inline admission, accounting, reconciliation, lock lifetime and terminals. Leave chupa/__main__.py and tests/test_daemon_composition.py unedited. Reuse the existing production composition harness from the unchanged preservation suite to calibrate raising construction/run or consumption probes: prove deliberate wiring raises and ordinary graph construction plus CLI run/drain never touches the new boundary. Daemon import absence is no longer evidence after scheduler activation. Do not activate background task startup, CLI control routing, dispatch pause, kill, admission/storm holds or serve.

## Scope fence
- chupa/daemon.py
- tests/test_daemon_tasks.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py` exits 0 and proves every named own-entry invariant, exact record custody and behavioral dormancy through the real dormant component and calibrated production probes.
2. `uv run pytest tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py` preserves bootstrap run/drain inline admission, accounting, reconciliation, lock lifetime and terminals with all preservation suites unchanged.
3. `uv run pytest -q` exits 0 with no test removed or skipped and no production activation.

## Verification
```
uv run pytest tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_scheduler.py tests/test_mergequeue.py tests/test_triage.py tests/test_cli.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Stop with premise_failed if a criterion forces a path outside the fence or the governing entry omits a needed fact; name the missing contract for section 11.4 hardening. Refuse invented records, replacement graphs and production behavior outside this admission.

## Time budget
- expected: 60m
- stuck: 90m
