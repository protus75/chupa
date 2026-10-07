---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-10
- kill-signal-journal

## Context
- chupa/daemon.py
- chupa/driver.py

## Plan contract
- 19.I
- 19.P3.kill-executor-abort
- section 20
- section 6

## Goal / Why
Dormant executor abort atomicity. Build only the explicit dormant boundary over the merged owners and seams.

## Scope in / Scope out
- **Owner:** `chupa/driver.py` owns aborting and observing its active stage invocation, including the LLM effect, optional review wait, and stuck-budget timer. Add an async `Driver.abort_current()` operation without changing existing construction or `run` call signatures. `chupa/daemon.py` owns a dormant executor-abort boundary supplied with that operation by its caller; it awaits executor unwind and owns no worker cancellation. No new module is introduced. The synchronous `LLM.abort_current()` remains the section 6 external-writer seam, not an Effect or a second model-call path.
- **Records:** Active invocation and its call/timer futures are in-memory ownership only, cleared after cleanup; no counter file, durable abort flag, or new constant is introduced. Kill authorization remains the predecessor `kill-signal-journal` boundary's current-lifecycle accepted decision, written by the lock-holding control consumer before abort is invoked. This boundary neither writes that decision nor invents an applied signal: its successful return supplies unwind evidence to the later activation, which records application only afterwards. Preserve section 6's existing LLM effect intent/completion envelopes and attempt/run-sequence keys, spool paths, cost capture, and write-seam redaction. An interrupted effect may leave an intent without completion; never fabricate a completion, successful StageResult, or terminal to close it. The executor boundary writes no journal record, ticket, cap consumption, harvest, or run terminal. Terminal/restart reconciliation and post-kill failure routing remain with their existing owners and later activation rows.
- **Observable:** Explicit abort targets only the invocation currently owned by this Driver. With none active it is a no-op; after a completed invocation it cannot affect a later one. For an active invocation, call synchronous `LLM.abort_current()` BEFORE cancelling the invocation or its call/timer futures. Await and observe their unwind, retrieving expected cancellation/abort exceptions, before clearing ownership or returning. Cancellation alone is insufficient: a cancellation-resistant writer must be stopped through the LLM seam, and the process-exec seam still owns subprocess reaping. No harvest or worktree cleanup may rely on abort completion until these waits finish. A failure to stop or observe the executor propagates rather than reporting successful abort.

  Repeated or concurrent aborts of the same active invocation share its cleanup and do not cancel cleanup again or reach a subsequent invocation. Repeated cancellation of an abort waiter must not release ownership while the executor still runs; finish the protected cleanup before propagating cancellation. If ordinary completion races abort, observe the actual completed invocation and leave no pending timer or unobserved exception. External abort propagates cancellation from the active stage instead of converting it to timeout, infra_error, a re-prompt, or successful output. Preserve ordinary successful, provider-error, gate/re-prompt, and stuck-budget behavior: the existing timeout path still stops the external writer before returning timeout, and uses the same cleanup ownership rather than a parallel abort implementation. A later explicitly started stage can run normally; the lifecycle stopping latch belongs to activation, not to Driver.

  Construction is behaviorally dormant under `19.I`: real CLI `run`/`drain` and the production-composition harness do not invoke the new external abort boundary or bind it to control consumption. Existing timeout aborts remain active. `kill-cli-activation` later exposes the Driver through Stages/Pipeline/Runner and migrates this external-abort dormancy assertion; worker cancellation, failure suppression, and serve wiring remain their own rows.
- **Tests:** `tests/test_kill_executor_abort.py` adds `test_executor_abort_stops_writer_before_cancellation` (explicit dormant boundary driving a real Driver with a cancellation-resistant fake; abort-before-cancel, no mutation after return, call/timer observed), `test_executor_abort_waits_for_unwind` (barrier-held cleanup, ownership retained, no premature completion), `test_executor_abort_is_atomic_under_repeated_cancellation` (concurrent/repeated abort and waiter cancellation, one protected cleanup), `test_executor_abort_idle_and_completion_race` (idle/completed no-op, completion race, cleared ownership, no leaked futures or exceptions, later stage unaffected), `test_external_abort_does_not_reprompt_or_report_success` (active LLM and optional review waits, cancellation propagated, no fabricated completion/terminal or extra call), and `test_executor_abort_is_dormant` (calibrated raising external-abort probe, real CLI run/drain and production graph leave it untouched). Verify unchanged timeout, prompt/spool, provider-error, retry, cost, and redaction behavior with `uv run pytest tests/test_kill_executor_abort.py tests/test_driver.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py`; these predecessor suites are preservation suites. Use injected clock/sleep/process/filesystem seams, disposable directories, and asyncio barriers, never real-model calls or wall-clock sleeps. Misordering abort/cancel or returning before unwind must make its named test fail.

AUTHORING CLOSURE: The registry floor needs no additions under 19.L rules 2-5. Existing fenced owners are Context; the new test is created and belongs in neither Context nor On-demand. Preservation suites run unchanged in Verification only, neither fenced nor embedded. No production signature or constructor changes; no public-operation allowlist or old production absence assertion needs migration. Historical seeding tests stay unchanged.

Authoring rg across chupa/, eval/ and tests/ covered abort_current, Driver construction/run/race/_kill, timeout ownership, optional review waits, cancellation handling, ControlInbox, ControlProjection.kill_requested, control_inbox, PauseConsumer, DaemonTasks, public-operation allowlists, not hasattr and production absence assertions. Existing LLM.abort_current callers are providers/fakes and Driver._kill. Driver.race also serves chupa/requisition.py; keep its signature and behavior. Driver construction and run signatures remain unchanged, so their callers need no edits. The timeout path and external abort must share cleanup ownership. No allowlist pins Driver or daemon operations. ControlInbox already validates and folds kill; reuse it rather than duplicating decisions. Existing tests/test_control.py kill assertions preserve projection-only behavior and altered decided-file inertia; no assertion flip is earned. The merged production harness is tests/test_daemon_composition.py (CoreRig and LiveDrain); read it as a read-only reference and exercise its real graph from the new suite without changing or embedding this preservation suite. chupa.daemon is already reachable, so import absence is not dormancy evidence.

Calibrate raising probes: deliberately supplied kill-application/external-abort wiring must trip its probe, while real CLI run/drain and ordinary production composition leave it untouched. Preserve the invocation's shared admission/dispatch control consumer, independent holds, and bootstrap inline admission. Out: worker stop, failure suppression, concurrent polling, CLI kill activation, background startup, serve wiring, replacement control implementation or abort path, new modules, records, constants, config and frontmatter.

## Scope fence
- chupa/daemon.py
- chupa/driver.py
- tests/test_kill_executor_abort.py

## Acceptance criteria
1. `uv run pytest tests/test_kill_executor_abort.py tests/test_driver.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py` exits 0 with every own-entry named invariant test, calibrated raising dormancy probes, and preserved predecessor behavior.
2. `tests/test_kill_executor_abort.py` proves the complete Owner, Records, Observable and Tests contract above, including exact custody, ordering, identity, crash/cancellation edge behavior and behavioral dormancy through real CLI run/drain and production composition.
3. `uv run pytest -q` exits 0 without removed or skipped tests; no production kill wiring, worker control, background task or serve activation is introduced.

## Verification
```
uv run pytest tests/test_kill_executor_abort.py tests/test_driver.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or contradictory entry unit for section 11.4 hardening if a needed fact is omitted or a criterion forces an unearned path outside the fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
