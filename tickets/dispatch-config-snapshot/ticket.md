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
- dispatch-admission-boundary

## Context
- chupa/config.py
- chupa/runner.py
- chupa/__main__.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.dispatch-config-snapshot
- section 15

## Goal / Why
Build dormant per-admission configuration capture so each callback sees one detached recursively immutable snapshot and the next admission observes validated edits.

## Scope in / Scope out
- **Owner:** `chupa/config.py` owns `snapshot_config(config)`, a detached, recursively immutable `Config` snapshot preserving existing field-attribute access. `chupa/daemon.py` owns `snapshot_dispatch(load, bind)`, a dormant adapter returning the existing `chupa.runner.Dispatch`. Its injected zero-argument `load` returns the current validated `Config`; its injected `bind(snapshot)` returns the ticket callback for that snapshot. Compose this adapter as the callback of `DaemonAdmission`, so capture happens inside its serial slot, not while a ticket waits. No new module is introduced. The existing loader remains the sole parser and validator; `DaemonAdmission` retains task ownership, single-flight ordering, and cleanup. Construction changes only the row's `chupa/daemon.py`, `chupa/config.py`, and `tests/test_daemon_config.py`; production wiring belongs to `scheduler-activation`.
- **Records:** A snapshot contains every field of the supplied `Config`, including nested defaults and unset optional values, with the same keys and values as `config.model_dump(mode="python")`. Nested model records retain their field-attribute access but refuse assignment; dictionaries become read-only mappings, lists become tuples recursively, and scalar values, `Path` values, and `None` retain their values. No mutable container or model is shared with the source. Top-level replacement, nested record replacement, mapping insertion/deletion, and sequence mutation are refused; a shallow copy or a frozen outer model with mutable children is insufficient. Read provider names, auth environment-variable names, models and limits, ordered routing candidates, review triggers and severities, merge strategies, scheduler limits, caps, and every other existing config field without selecting a subset or adding defaults. Preserve path resolution, list order, schema handshake, explicit-null refusal, unknown-key refusal, reference checks, and the current `kind: api` refusal by using `load_config` before capture, never reparsing or revalidating the immutable representation. The snapshot helper is the sole constructor of the view; the dispatch adapter owns its per-call lifetime. No config key, frontmatter value, engine constant, journal event, signal, body key, artifact, snapshot identifier, or durable writer is added.
- **Observable:** Each explicitly invoked adapted dispatch calls `load` once, captures once, calls `bind` once with that snapshot, and awaits the resulting callback once with the original `Ticket`. It returns the callback's terminal string unchanged. A running callback retains the same snapshot for its entire lifetime: later source-model mutation, nested-container mutation, or a config-file edit cannot change it. The next admitted dispatch loads afresh and observes valid edits, including ceiling, routing, and severity changes. A waiting dispatch captures only after the preceding callback fully unwinds. A load or capture failure propagates before binding or invoking the ticket callback; there is no cached fallback to the previous valid config. Binding failures, callback exceptions, and cancellation propagate through `DaemonAdmission` without leaking ownership or preventing the next dispatch. This adapter writes no dispatch accounting, retries, terminals, or diagnostics.

  Construction is dormant under `19.I`: production CLI `run` and `drain` keep their existing composition and do not call `snapshot_dispatch` or `snapshot_config`. Test the real CLI composition root with its existing injected pipeline seam and raising probes on the new operations; prove the probes fail when the operations are wired. The daemon remains absent from the transitive CLI import closure, recognizing both import idioms. Preserve `load_config`'s return type and existing public signatures, including `DaemonAdmission.dispatch(ticket)` and `Dispatch = Callable[[Ticket], Awaitable[str]]`. This row does not globally freeze the mutable config models, add a watcher, change the bootstrap drain, or activate daemon composition. The later scheduler activation owns production use and migration of dormancy assertions.
- **Tests:** `tests/test_daemon_config.py` names `test_snapshot_preserves_all_validated_config_values` (recursive comparison with the complete Python-mode dump, resolved paths, defaults, unset optionals, and sequence order); `test_snapshot_is_recursively_immutable_and_detached` (top-level and nested assignment, mapping insertion/deletion, sequence mutation, and mutations of the original models and containers); `test_dispatch_captures_once_and_keeps_snapshot_until_completion` (one load/capture/bind/callback, original ticket, unchanged terminal, config-file and source edits during a blocked callback); `test_next_dispatch_observes_valid_config_edits` (ceiling, route, and severity changes through the real loader); `test_waiting_dispatch_captures_after_admission` (two calls through real `DaemonAdmission`, injected barriers, second load only after first cleanup); `test_invalid_reload_never_binds_or_uses_stale_config` (missing file, invalid YAML, explicit null, invalid schema, and valid recovery on the following dispatch); `test_snapshot_dispatch_unwinds_failures_and_cancellation` (load, bind, and callback errors, active and waiting cancellation, cleared ownership and successful subsequent dispatch); and `test_config_snapshot_is_dormant` (real CLI `run` and `drain`, discriminating raising probes, and the transitive import-closure scan). All callbacks and waits use injected seams and asyncio barriers, never real-model calls or wall-clock sleeps. Verification runs `uv run pytest tests/test_daemon_config.py tests/test_daemon_admission.py tests/test_config.py tests/test_cli.py tests/test_drain.py`; the last four are unchanged preservation suites, so construction requires no signature or caller migration outside the row's fence.

Read chupa/daemon.py from the worktree after dispatch-admission-boundary merges, before writing; it is sibling-created at authoring and belongs in neither Context nor On-demand. Preserve its dispatch(ticket) signature and ownership contract.

Out: activation, public signature or constructor changes, production caller changes, and all later registry machinery. Keep every preservation suite unchanged, Verification-only, neither fenced nor embedded.

## Scope fence
- chupa/daemon.py
- chupa/config.py
- tests/test_daemon_config.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_config.py tests/test_daemon_admission.py tests/test_config.py tests/test_cli.py tests/test_drain.py` exits 0, exercising every Owner, Records, Observable and named Tests obligation stated above through the real dormant components and injected seams.
2. `uv run pytest -q` exits 0 with no existing test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest tests/test_daemon_config.py tests/test_daemon_admission.py tests/test_config.py tests/test_cli.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject if either new snapshot operation is called in production, daemon enters the CLI import closure during construction, a snapshot shares mutable state or omits a Python-mode dump field, capture precedes admission, a stale reload fallback is used, or meeting a criterion requires an out-of-fence edit; return premise_failed naming any missing governing fact instead of inventing it.

## Time budget
- expected: 60m
- stuck: 90m
