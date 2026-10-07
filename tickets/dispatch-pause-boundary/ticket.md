---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-08

## Context
- chupa/daemon.py
- chupa/drain.py
- chupa/control.py
- tests/test_drain.py

## Plan contract
- 19.I
- 19.P3.dispatch-pause-boundary
- section 20

## Goal / Why
Construct a behaviorally dormant pause checkpoint before every next-offer accounting action, so a held dispatch spends no retry unit and binds no snapshot.

## Scope in / Scope out
- **Owner:** `chupa/daemon.py` owns the dormant pause checkpoint at `DaemonAdmission.dispatch`; `chupa/drain.py` owns its placement before the drain's durable offer accounting. No new engine module is introduced. Both accept an injected zero-argument async `before_dispatch` callback returning `None`, optional at construction/entry so existing callers retain their behavior. The callback consumes pending control requests and awaits release while the current lifecycle's pause projection is held; supply it explicitly to exercise this construction. The existing control inbox owns decisions and identity matching; this boundary neither duplicates that algorithm nor opens another journal writer. Production callback binding and CLI pause/resume routing belong to `pause-resume-activation`.
- **Records:** Reuse the control inbox's accepted `CONTROL_DECISION` records and lifecycle/hold projection from `19.P3.control-inbox`: accepted pause establishes the request id as hold identity; only accepted resume for that lifecycle and that exact hold releases it. Stale/rejected decisions mutate nothing; accepted decisions are folded in journal order, latest-wins. The supplied callback retains ownership of consumption and wakeup; the boundary stores no independent durable pause flag, decision, processed marker, or hold identity. A paused wait must continue to permit consumption of resume requests, using injected async wakeup rather than a wall-clock polling loop.

  Preserve the existing drain writers and shapes. `caps.consume` writes `EventType.CAP_CONSUMED` with envelope `ticket: <stem>`, `key: null`, body `{cap: retry, ticket_sha: <committed ticket blob SHA>}`, optionally `rung: {tier: <existing tier>, effort: <existing effort>}` from the prior terminal. `_Drain._run_one` writes `EventType.STATE_TRANSITION` with envelope ticket stem, null key, body `{to: running, ticket_sha: <same SHA>}`. A normal re-offer draws exactly one retry unit before `running`; a fresh offer, changed-ticket premise re-offer, or released `spec_gap_hold` draws none, preserving the existing lineage-scoped cap fold. `_Drain._select`'s machine keep remains the existing signal `{signal: reject_verdict, verdict: keep, actor: machine}` for the stem. Intake, reconcile, runner, and merge retain their writers; the boundary adds no event type, signal, body key, frontmatter value, artifact, configuration key, or constant.
- **Observable:** Await the checkpoint before ANY durable accounting for the next offer, including selection's machine keep, retry-cap consumption, the `running` transition, and dispatch-owned effects. In the drain, a wrapper around the final dispatch callback is too late: the checkpoint must precede `_select`'s offer mutations and `_run_one`'s accounting. Re-read eligibility and journal-derived budget after a paused wait; never dispatch a stale selection or draw against a stale budget. Complete awaited offer preparation before the final checkpoint and perform retry/running accounting without an intervening await after it returns. While held, no retry draw, running transition, snapshot capture, or dispatch callback starts. Cancellation or failure of the checkpoint propagates before those actions and leaves no fabricated terminal or spent retry unit.

  In `DaemonAdmission`, await the checkpoint inside the single-flight slot before creating the owned invocation task or binding its dispatch snapshot. An in-flight dispatch finishes normally when a later pause arrives; pause governs the next offer and never preempts active work. Cancelled waiters never dispatch, ownership clears after cleanup, and successful release preserves the original Ticket, callback terminal, retry-before-running order, and existing cap exceptions. Construction is behaviorally dormant under `19.I`: ordinary production graph construction and CLI `run`/`drain` supply no pause callback, consume no controls, and acquire no pause hold. Calibrate raising checkpoint probes through explicit wiring and prove ordinary production paths leave them untouched. `pause-resume-activation` migrates this dormancy assertion; kill execution, worker stop, admission/storm holds, and continuous serve remain their later rows' contracts.
- **Tests:** `tests/test_daemon_pause.py` names `test_pause_checkpoint_precedes_dispatch_and_snapshot` (single-flight checkpoint, no invocation or snapshot while held, original ticket and terminal after release); `test_pause_does_not_preempt_active_dispatch` (active work finishes, next offer waits); `test_only_matching_resume_releases_pause` (real dormant inbox, premature/stale/wrong-hold resumes, latest accepted pause/resume, durable decision visible before release); `test_checkpoint_failure_and_cancellation_leave_no_dispatch` (blocked and queued cancellation, raised failure, cleared ownership and later successful offer); and `test_dispatch_pause_boundary_is_dormant` (production composition harness or real CLI root, calibrated probes, no production checkpoint/control consumption). `tests/test_drain.py` adds `test_pause_precedes_fresh_offer_accounting`, `test_pause_precedes_retry_cap_draw`, `test_pause_precedes_machine_keep`, `test_pause_release_rechecks_eligibility_and_budget`, `test_pause_checkpoint_failure_spends_no_retry`, and `test_pause_preserves_free_premise_and_spec_gap_reoffers`, exercising the real drain with an explicitly supplied checkpoint and journal assertions before and after release. Verify exact retry/running ordering, optional rung preservation, no effects while held, and unchanged cap lineage and free re-offer cases. Run `uv run pytest tests/test_daemon_pause.py tests/test_drain.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_control.py tests/test_daemon_composition.py`; the last four suites are unchanged preservation suites once their predecessor machinery merges. Use injected seams, disposable directories, scripted dispatch, and asyncio barriers, never real-model calls or wall-clock waits.

AUTHORING CLOSURE: DaemonAdmission(dispatch), snapshot_dispatch(load, bind), daemon_core and drain(checkout, dispatch, reexec=...) retain existing calls through optional before_dispatch. Greps across chupa/, eval/ and tests/ found no required caller or public allowlist migration beyond the registry floor. CLI run/drain currently bypass DaemonAdmission; control_inbox is explicit and dormant. The sibling creates no file to embed here. Use real dormant inbox control_inbox with ControlProjection, consume() and recover() through injected files/read/holds/apply; do not reimplement identity matching. Daemon import absence is no longer evidence: calibrate raising before_dispatch probes through explicit wiring over the merged production harness, and show ordinary CLI run/drain and graph construction leave them untouched. Read that harness from the worktree for idiom; it is an unchanged preservation suite, neither fenced nor embedded.

Preserve bootstrap inline admission, accounting, reconciliation, lock lifetime and terminals. Leave production binding and CLI routing to pause-resume-activation. Do not implement kill, admission/storm holds, background startup or serve.

## Scope fence
- chupa/daemon.py
- chupa/drain.py
- tests/test_daemon_pause.py
- tests/test_drain.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_pause.py tests/test_drain.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_control.py tests/test_daemon_composition.py` exits 0 with every own-entry named invariant test exercising the real boundary and injected seams.
2. `tests/test_daemon_pause.py` and `tests/test_drain.py` prove behavioral dormancy, no invocation/snapshot/accounting while held, failure/cancellation cleanup, real inbox identity matching, fresh selection/budget after release, exact retry-before-running and free re-offers.
3. `uv run pytest tests/test_daemon_pause.py tests/test_drain.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_control.py tests/test_daemon_composition.py` keeps the listed unchanged preservation suites green; preserve bootstrap inline admission, accounting, reconciliation, lock lifetime and terminals.
4. `uv run pytest -q` exits 0 without removing or skipping tests; no kill, admission/storm holds, background startup or serve activation.

## Verification
```
uv run pytest tests/test_daemon_pause.py tests/test_drain.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_control.py tests/test_daemon_composition.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the contract for section 11.4 hardening if a governing entry omits a needed fact or the criteria require an unearned path outside the fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
