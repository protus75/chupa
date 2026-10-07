---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-05

## Context
- chupa/daemon.py
- chupa/scheduler.py
- chupa/watcher.py
- chupa/__main__.py
- tests/test_scheduler.py
- tests/test_daemon_admission.py
- tests/test_daemon_config.py
- chupa/runner.py
- chupa/stages.py
- chupa/driver.py
- chupa/providers.py
- chupa/redact.py
- chupa/gates.py
- chupa/caps.py

## Plan contract
- 19.I
- 19.P3.scheduler-activation

## Goal / Why
Activate the production daemon core through the real CLI composition root, without changing bootstrap run/drain dispatch. The scheduler-activation registry row is deep: true, so this ticket starts high/high under 19.L.

## Scope in / Scope out
- **Owner:** `chupa/daemon.py` owns the production daemon-core factory composing the existing `Scheduler`, `Watcher`, `DaemonAdmission`, and `snapshot_dispatch`; `chupa/__main__.py` owns its composition-root binding of checkout, config loader, pipeline binding, and injected seams. The in-process harness in `tests/test_daemon_composition.py` calls that production root builder, never constructs a parallel test graph. `chupa/scheduler.py` retains selection and backpressure; `chupa/watcher.py` retains debounce and parsing; `chupa/config.py` retains validation and snapshot construction. `chupa/runner.py` owns factoring production provider preparation into `async prepare_pipeline(checkout) -> Dispatch`, shared by the synchronous bootstrap `pipeline` and the admitted daemon callback; it retains `bind(checkout, llm)` as the sole Driver/StageContext binding. `chupa/runner.py`, `chupa/stages.py`, `chupa/driver.py`, and `chupa/providers.py` own accepting `ConfigSnapshot` in their config consumers; `chupa/redact.py`, `chupa/gates.py`, and `chupa/caps.py` own the corresponding downstream read-only consumers. No new engine module is introduced. This core is the graph later extended and driven by `serve-activation`; bootstrap `run` and `drain` retain their existing dispatch, retry accounting, reconciliation, lock lifetime, and inline merge admission.
- **Records:** Compose one shared journal and one instance of each core component. Wire `Watcher.publish` to `Scheduler.update`, `Watcher.remove` to `Scheduler.remove`, and `Scheduler.dispatch` to `DaemonAdmission.dispatch`, whose callback is `snapshot_dispatch(load, bind)`. The root supplies ticket reads returning text or `None` for a removed file, change delivery carrying ticket stems, the committed plan for `parse_ticket`, `Clock`, `Sleep`, and a debounce duration in seconds; preserve the watcher's existing injected interface without adding a watcher library or config key. The dispatch loader uses the same explicit `--config` path or checkout-relative `config.yaml` and the existing `load_config`; binding receives the complete detached immutable snapshot and returns the existing `Dispatch = Callable[[Ticket], Awaitable[str]]`. The root's synchronous `bind(snapshot)` creates a dispatch-local `Checkout` with `dataclasses.replace(checkout, config=snapshot)`, retaining its repo, env, executor, Git, journal, filesystem, clock, and sleep seams. Its returned async callback awaits `runner.prepare_pipeline` on that checkout, then awaits the resulting Dispatch with the original Ticket. The daemon root supplies a preparation seam `Callable[[Checkout], Awaitable[Dispatch]]` defaulting to `runner.prepare_pipeline`; its default binding uses this production preparation, never the synchronous `runner.pipeline` inside an admitted task. All dispatch-local pipeline consumers receive that same snapshot; snapshot capture occurs inside admission, once per admitted call, never at graph construction or while waiting.

  `Checkout.config`, `StageContext.config`, `Driver.from_config`, and provider config consumers explicitly accept `Config | ConfigSnapshot`. Provider routing, `Served.provider`, adapter construction, child-environment filtering, redactor construction, merge severity, and cap/rung reads also accept the snapshot's nested immutable records (including provider and caps records), mappings, and tuples. They read existing field attributes and sequence order without mutation, conversion back to `Config`, revalidation, or a second snapshot. `load_config` continues returning validated mutable `Config`; its schema and the existing `ConfigSnapshot` representation are unchanged.

  `runner.prepare_pipeline` constructs `ProviderLLM` from that checkout's config, awaits its existing `preflight()`, raises the existing `runner.Refusal` with the provider diagnostics and paved road on nonempty problems, and only on success calls `runner.bind` to construct Driver and StageContext. In daemon dispatch this all runs inside `DaemonAdmission`'s owned task after capture and before `drive` or any ticket-stage work; it runs once for each admitted snapshot, never at graph construction or while waiting. No admitted code calls `asyncio.run`. The existing synchronous `runner.pipeline(checkout) -> Dispatch` delegates to this same preparation using `asyncio.run` only at the outer bootstrap CLI binding before its run/drain event loop, preserving `Pipeline = Callable[[Checkout], Dispatch]`, startup preflight refusal, and the existing injected pipeline seam. There is one provider/preflight/stage preparation implementation, with no cached provider or stale preflight result reused across daemon admissions.

  Parsed `Ticket` records retain `stem`, `frontmatter.state` (`draft`, `confirmed`, `rejected`, `merged`), `frontmatter.priority` (`P0` through `P3`), and tuple `depends`. Selection reuses `drain.SETTLED` (`merged`, `already_satisfied`), `last_states`, `reject_queue`, `authored_at`, and `sort_key`: read `state_transition` body `to`, the existing Reject-routing/verdict records, and the first `ticket_intake` signal's envelope `ts`; order by priority, known age before missing age, oldest timestamp, then stem. The caller supplies current journal-derived quarantine/drought sets, completed-but-unmerged count, and existing `scheduler.max_unmerged` (default `2`), with selection re-reading them before each dispatch. Their policy owners remain unchanged. Watcher parse failures keep their sole writer, `chupa/watcher.py`, and constant `WATCHER_PARSE_FAILURE = "watcher_parse_failure"`: `EventType.SIGNAL`, envelope `ticket: <stem>`, `key: null`, body `{signal: watcher_parse_failure, path: tickets/<stem>/ticket.md, reason: <nonempty diagnostic>}`. Pending/cache/active/task references are memory-only. The callback's terminal is unchanged at admission; `Scheduler.dispatch_next` retains its selected-`Ticket` or `None` result. Runner, drain, intake, and merge remain the sole writers of their existing accounting, intake, and terminal records. Activation adds no event type, signal, body key, frontmatter value, artifact, config key, or engine constant.
- **Observable:** The daemon, scheduler, and watcher become reachable in the transitive production CLI import closure, recognizing both import idioms. Calling the production root builder constructs the real graph without dispatching host work, loading a per-dispatch snapshot, or starting background consumers. Explicitly drive its watcher and scheduler through injected delivery and callbacks: debounced valid updates alter the next selection, an invalid edit preserves the last-known-good record and position, an invalid new stem stays absent, and removal drops pending work. A P0 edit never preempts the active ticket. Concurrent selections remain single-flight through callback cleanup; success, exception, and cancellation clear ownership before another dispatch, and a cancelled waiter never invokes a callback. Running work keeps its snapshot despite later config edits; the next admission observes valid edits, and invalid reload fails before binding without a stale fallback. Existing eligibility, hold release, age ordering, and backpressure behavior is preserved through this graph.

  Migrate `test_scheduler_and_watcher_are_dormant` in `tests/test_scheduler.py` and the daemon-absence import-closure assertions in `test_daemon_admission_is_dormant` and `test_config_snapshot_is_dormant` to positive production reachability and graph evidence; keep every component behavior assertion and the bootstrap CLI preservation checks. The activation seed adds `tests/test_daemon_config.py` to its fence and Context under `19.L` ACTIVATION/CONTRADICTED TESTS because the predecessor pins daemon import absence there. Under `19.L` CALLER CLOSURE it also adds `chupa/runner.py`, `chupa/stages.py`, `chupa/driver.py`, `chupa/providers.py`, `chupa/redact.py`, `chupa/gates.py`, and `chupa/caps.py` for the production binding and snapshot-consumer changes, plus every direct caller found by the authoring-time grep; these existing paths enter Context/on-demand under its size rule, and each addition is recorded in the seeding test. The registry fence is the floor. Background task ownership, control, pause/kill, merge-queue/Rework activation, daemon admission routing, and the continuous `serve` verb remain their named later rows' contracts.
- **Tests:** `tests/test_daemon_composition.py` adds `test_production_core_uses_real_snapshot_pipeline` (default production preparation, real ProviderLLM, adapters, Driver and StageContext, snapshot identity at each config consumer, provider routing, secret filtering/redaction, severity and caps, original Ticket and terminal); `test_production_core_awaits_preflight_inside_admission` (running event loop, capture before provider construction and one awaited preflight before bind/stage work, no preparation at construction or for a waiting/cancelled waiter, fresh preparation after a config edit); and `test_production_core_unwinds_preflight_refusal_and_cancellation` (nonempty problems retain the existing Refusal and paved road, raised errors and cancellation during preflight propagate, no stage work starts, ownership clears after cleanup, and a subsequent valid admission succeeds). These tests retain the real preparation, preflight, and bind functions and use scripted process/filesystem seams for provider version/model probes and calls; stop before host work. Scripted pipeline callbacks alone are insufficient evidence for these three obligations. Existing bootstrap CLI/provider tests preserve preflight-before-run/refusal behavior and the synchronous injected Pipeline contract. `tests/test_daemon_composition.py` also names `test_production_root_builds_daemon_core_without_running_work` (real root factory, shared journal and correctly connected components, no callback, snapshot load, or background task at construction); `test_production_core_dispatches_through_admission_and_snapshot` (original ticket reaches the existing pipeline binding exactly once, one immutable snapshot shared by its consumers, terminal preserved at admission); `test_production_core_reprioritizes_without_preemption` (blocked active callback, debounced edit and new P0, next pick changes only after cleanup); `test_production_core_preserves_last_good_and_removes_tickets` (invalid existing/new input, exact parse-failure record, valid recovery and removal); `test_production_core_preserves_eligibility_order_and_backpressure` (settled dependencies, Reject/quarantine/drought holds and release, distinct intake ages, missing age, priority/stem tiebreaks, count at and below the limit); `test_production_core_reloads_config_only_after_admission` (waiting request captures after cleanup, active snapshot unchanged, next valid edit observed, invalid reload never binds); `test_production_core_unwinds_errors_and_cancellation` (callback/load/bind failures, active and waiting cancellation, no surviving owned task, subsequent dispatch succeeds); and `test_daemon_core_is_reachable_from_cli` (positive transitive closure, with a removed import edge proving the assertion discriminates). Preserve the predecessor component tests while migrating their negative closure assertions. Verification runs `uv run pytest tests/test_daemon_composition.py tests/test_scheduler.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_config.py tests/test_cli.py tests/test_drain.py tests/test_providers.py tests/test_driver.py tests/test_stages.py tests/test_gates.py tests/test_caps.py`; existing suites outside the activation fence run unchanged as preservation suites. Use injected seams and asyncio barriers, with scripted pipeline callbacks for scheduler-only cases, never real-model calls, host work, or wall-clock waits. Later activations extend this same production harness.

Transition closure: tests/test_daemon_config.py is added under ACTIVATION/CONTRADICTED TESTS for test_config_snapshot_is_dormant. The seven added production files chupa/runner.py, chupa/stages.py, chupa/driver.py, chupa/providers.py, chupa/redact.py, chupa/gates.py and chupa/caps.py are CALLER CLOSURE for the async preparation binding and read-only immutable config consumers. Preserve existing public component signatures and the synchronous bootstrap Pipeline seam. Every existing fenced file is embedded Context; tests/test_daemon_composition.py is created and is neither Context nor On-demand. Unfenced Verification suites are unchanged preservation suites, neither fenced nor embedded.

Out: background task startup, control, pause/kill, merge-queue/Rework activation, daemon-mode merge routing and the continuous serve verb; each remains its later registry row.

## Scope fence
- chupa/daemon.py
- chupa/scheduler.py
- chupa/watcher.py
- chupa/__main__.py
- tests/test_scheduler.py
- tests/test_daemon_admission.py
- tests/test_daemon_composition.py
- tests/test_daemon_config.py
- chupa/runner.py
- chupa/stages.py
- chupa/driver.py
- chupa/providers.py
- chupa/redact.py
- chupa/gates.py
- chupa/caps.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_composition.py` exits 0 over every named production-core obligation in Scope in / Scope out, exercising the real root, real snapshot preparation/provider/preflight/bind path, watcher and scheduler through injected seams before host work.
2. `uv run pytest tests/test_scheduler.py tests/test_daemon_admission.py tests/test_daemon_config.py` exits 0 after migrating only the three predecessor negative import-closure assertions to discriminating positive production reachability and graph evidence, retaining component behavior and bootstrap CLI checks.
3. The complete Verification command `uv run pytest tests/test_daemon_composition.py tests/test_scheduler.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_config.py tests/test_cli.py tests/test_drain.py tests/test_providers.py tests/test_driver.py tests/test_stages.py tests/test_gates.py tests/test_caps.py` exits 0, preserving unchanged bootstrap dispatch, preflight/refusal, reconciliation, retry accounting, lock lifetime and inline merge; all dispatch-local consumers use the same immutable snapshot captured once after admission.
4. `uv run pytest -q` exits 0 with no existing test removed or skipped and no new durable record or config key.

## Verification
```
uv run pytest tests/test_daemon_composition.py tests/test_scheduler.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_config.py tests/test_cli.py tests/test_drain.py tests/test_providers.py tests/test_driver.py tests/test_stages.py tests/test_gates.py tests/test_caps.py
uv run pytest -q
```

## Definition of rejected
Reject a parallel test graph, scripted-only evidence for real preparation obligations, snapshot capture/preflight at construction or while waiting, asyncio.run inside admitted work, mutable config reconstruction, missing predecessor migration, changed bootstrap behavior, real-model calls, host work, wall-clock waits, or any edit outside this fence. Missing governing facts return premise_failed naming the entry unit for section 11.4 hardening.

## Time budget
- expected: 90m
- stuck: 150m
