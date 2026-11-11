---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/providers.py::ProviderLLM.preflight
- chupa/providers.py::CliAdapter.invoke
- chupa/providers.py::CliAdapter.abort

## On-demand
- tests/integration/test_providers.py
- tests/integration/test_watchdog.py

## Goal / Why
Every drain, serve and run start runs provider preflight before any work, and the drain restarts itself after every merge that changes engine code, so preflight runs again for each such ticket. Preflight runs strictly one step at a time: a `--version` and a `pnpm view` per provider CLI, then one probe call per routed (provider, model) pair. On 2026-11-11 at 10:13 that was two claude probes (8s) and four codex probes (20s), 28s in all, while every probe is independent of the others. The capture files `.chupa/state/spools/providers/preflight/{codex-0001..0004,claude-0001..0002}` show the serial timeline.

When this ticket is done, preflight starts all probes at once. The version lookups (about 2s) stay serial. A start then waits about as long as the slowest single probe plus the version lookups (about 9s that day), not the sum of every probe. Results, problems and notices stay exactly as today.

## Scope in / Scope out
- In: `chupa/providers.py::ProviderLLM.preflight`:
  - The per-provider `--version` and `pnpm view` calls stay serial and unchanged.
  - All probe calls for the routed (provider, model) pairs run concurrently, each still probed once.
  - Calls start in today's order: each adapter's `--version` before its `pnpm view`, adapters in adapter order, every version lookup finished before the first probe starts, and probes started in routing order.
  - An exception from a version lookup or a probe call reaches the caller unchanged, never wrapped in an `ExceptionGroup`. Cancelling preflight cancels every running probe and waits for each to finish, leaving no child task.
  - `problems` and `preflight_notices` keep today's content and order: providers in adapter order, probes in routing order, whatever order the calls finish in.
  - `session.preflight_passed()` is called only when no probe failed, as today.
- In: `CliAdapter` tracks a set of running process groups instead of the single `_pgid`. `_spawned` adds a group, the call's end removes it, and `abort()` kills every group in the set. Today a second concurrent call on one adapter overwrites the first call's group, so an abort could miss a running probe. `tests/integration/test_providers.py` and `tests/integration/test_watchdog.py` read `_pgid` and change to the set.
- In: new `tests/unit/test_preflight_parallel.py`, which runs without disk or process (fake exec and fake `FileSystem`).
- Out:
  - Skipping or caching preflight across a restart.
  - Admission limits (`limits.concurrency`) for real work calls. Probes already bypass admission and stay so.
  - Which pairs are probed.

## Scope fence
- chupa/providers.py
- tests/integration/test_providers.py
- tests/integration/test_watchdog.py
- tests/integration/test_daemon_composition.py
- tests/unit/test_preflight_parallel.py

## Acceptance criteria
1. `tests/unit/test_preflight_parallel.py`, with a fake exec whose probe calls each wait on a shared barrier that opens only when every routed probe has started (and a 2s timeout that fails the test), and a fake session recording `preflight_passed` calls: `preflight()` returns `[]`, and `preflight_passed` was called exactly once. A serial preflight never opens the barrier and times out instead.
2. `tests/unit/test_preflight_parallel.py`: with probes finishing in reverse routing order and two of them refused, `problems` lists the two refusals in routing order, not finish order, and `preflight_passed` was not called. With two stale CLIs, `preflight_notices` lists them in adapter order.
3. `tests/unit/test_preflight_parallel.py`: with two calls running at once on one adapter, `abort()` kills both process groups, not only the last spawned. After both calls end, the adapter's running set is empty.
4. The preflight tests in `tests/integration/test_providers.py` (lines 452-478) pass unchanged. So do `tests/integration/test_fixture_host.py::test_fixture_cli_adapter_roundtrip` (call start order), `tests/integration/test_daemon_composition.py::test_production_core_awaits_preflight_inside_admission` (probes recorded in routing order; it changes only at line 794, where the `asyncio.current_task() is rig.core.admission.task` assertion keeps applying to the version-lookup calls, and for probe calls, which now run in child tasks, it asserts instead that the admission task is still the active owner: `rig.core.admission.task` not done and `rig.core.admission.active` set), `tests/integration/test_daemon_composition.py::test_production_core_unwinds_preflight_refusal_and_cancellation` (the same error object reaches the caller, no child task left after cancel), and the `preflight_passed` users in `tests/integration/test_provider_cooldown_failover.py`.
5. The `_pgid` reads change to the set: the callback and unwind tests at `tests/integration/test_providers.py:843`, `:889` and `:946` and `tests/integration/test_watchdog.py:565` assert the adapter's running set is empty after the call. The tests at `tests/integration/test_providers.py:921` and `tests/integration/test_watchdog.py:556` assert `process.pgids[-1]` is in the set, not equal to a single `_pgid`.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A routed (provider, model) pair is probed more than once, or not at all.
- `problems` or `preflight_notices` order depends on which call finishes first.
- Preflight is skipped, cached, or made optional.

## Time budget
- expected: 30m
- stuck: 60m
