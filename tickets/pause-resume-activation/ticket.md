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
- dispatch-pause-boundary

## Context
- chupa/daemon.py
- chupa/control.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_daemon_composition.py
- tests/test_control.py
- chupa/seams.py
- chupa/lockfile.py

## Plan contract
- 19.I
- 19.P3.pause-resume-activation
- section 20

## Goal / Why
Activate CLI pause/resume and the shared live drain pause consumer before all next-offer accounting, with durable identity-bound release and an idle locked no-op.

## Scope in / Scope out
- **Owner:** `chupa/__main__.py` owns the `pause` and `resume` CLI routing and the shared control composition factory. `chupa/control.py` retains ownership of request publication, validation, exactly-once decisions, and lifecycle/hold matching; `chupa/daemon.py` owns the production consumer and pause projection; `chupa/drain.py` binds that consumer to the lock-owning drain and the predecessor's `before_dispatch` checkpoint. No new module is introduced. Activate the machinery specified by `control-inbox` and `dispatch-pause-boundary`, rather than implementing another inbox or pause algorithm. At authoring, read those merged predecessors' public operations and every direct caller before choosing the activation wiring. The current pre-activation CLI has no `pause`/`resume` parser entries: section 20's direct locked behavior is the required contract, not evidence of an already implemented verb.
- **Records:** Reuse `<state_dir>/control/inbox/<request_id>.json` and its closed request shape `{request_id: str, lifecycle_id: str, verb: pause | resume | kill, hold_id: str | null}` from `control-inbox`. This activation publishes only `pause` and `resume`: pause has null `hold_id`; resume binds the exact current pause request id. The CLI publisher supplies a fresh filename-safe request id and reads the target engine's restart-unique lifecycle identity and current pause identity; it never substitutes a PID, checkout id, or lockfile diagnostic `instance_id`. On the live inbox route, a missing/unavailable lifecycle or a resume with no current pause is refused with the paved road to read the running engine's current control identity and submit a new request. Never queue an unbound resume for a future hold.

  The lock-holding engine publishes its lifecycle and current pause projection under `<state_dir>/control/active.json`. Its closed JSON representation is a live object `{lifecycle_id: nonempty str, hold_id: nonempty str | null}` or the literal JSON `null` when retired. `chupa/control.py` owns this discovery record's filesystem-seam writer; it is a projection, never decision authority. Publication, refresh, and retirement use the existing atomic `FileSystem.write(path, data)` operation; retirement writes `b"null\n"` to the same path, without unlinking it or adding a filesystem-seam operation. Publish only after acquiring the writer lock, refresh only after the corresponding durable decision, and retire before releasing the lock, including cancellation, failure, and self-upgrade handoff. A replacement engine generates a fresh lifecycle and overwrites the retired projection; stale discovery bytes or a publication racing replacement can at most produce a stale request, never retarget it. A publisher must establish lock contention before using discovery; missing, retired, or malformed discovery while the lock is held refuses with the road to retry after the running engine publishes its current identity, rather than writing a journal signal or guessing an identity. Do not change the lockfile diagnostic schema or use it as a liveness protocol.

  Retain `CONTROL_DECISION = "control_decision"` and its sole writer, the lock-holding consumer: `EventType.SIGNAL`, null ticket/key, body `{kind: control_decision, request_id: str, lifecycle_id: str | null, verb: pause | resume | kill | null, hold_id: str | null, decision: accepted | stale | rejected, reason: str}`. Decisions precede projection mutation and discovery refresh; accepted pause establishes its request id as hold identity, accepted matching resume clears it, and stale/rejected requests change nothing. Fold accepted decisions in journal order, latest-wins, and recover without duplicate decisions or application. Retain decided inbox files as inert input. No new journal event type, decision signal, cap, frontmatter field, or configuration key is introduced. Dispatch accounting keeps the exact predecessor writers and shapes, including retry-before-running and free premise/spec-gap re-offers.
- **Observable:** With an engine holding the lock, CLI pause/resume publish durable requests through the existing no-overwrite publication seam and return without acquiring the engine's writer role, writing the journal, mutating its pause state, or constructing a pipeline. Publication success means submitted, never falsely claims applied. The real drain constructs one consumer using its own journal, filesystem and clock seams, publishes its identity before offers, and supplies its pause checkpoint before all next-offer accounting. The checkpoint consumes pending requests and continues consuming matching resumes while held through an injected async wakeup; an accepted pause must not let the drain report quiescence merely because dispatch is held. Re-read selection and budget after release. Existing in-flight work completes normally; pause never cancels an invocation or suppresses its terminal or merge.

  With no engine running, pause/resume acquire the same writer lock and apply directly under section 20's contract. Direct application is a successful no-op: there is no lifecycle to pause or hold to resume. Return exit code 0 with `nothing running to pause` or `nothing running to resume`, then release the lock. Apart from the lockfile's existing diagnostic write, create or change no record: no lifecycle or request id is allocated, no inbox request or `CONTROL_DECISION` is written, no discovery projection is published or retired, and no pause flag or hold is persisted. Do not construct a consumer or pipeline. The next drain starts unpaused with its own fresh lifecycle; never leave a request to act on an unrelated later lifecycle. The lock acquisition decides this route, not the existence of discovery bytes, which the direct route ignores even if they name an old hold. A race losing that acquisition routes through the live inbox only after reading its identity; a missing identity refuses with a retry road. Keep ordinary `run` and bootstrap drain admission, reconciliation, caps, harvest, and self-upgrade ordering unchanged. Migrate the predecessor inbox and pause-checkpoint production-absence assertions to positive routing/consumption evidence, retaining their schema, durability, identity, and ordering assertions. Admission red-streak/tree-hash holds, storm holds, kill execution, owned worker tasks, and continuous `serve` activation remain their later rows' obligations.
- **Tests:** `tests/test_control_cli.py` names `test_live_pause_resume_publish_without_journal_write` (real CLI, held lock, durable exact request identities, no pipeline or second writer, submitted output); `test_resume_requires_current_pause_identity` (no hold, malformed/missing/retired discovery, no guessed or future release, paved refusals); `test_pause_resume_apply_directly_under_lock` (both verbs acquire and release the writer lock, exit 0 with the exact idle message, allocate no lifecycle/request identity, construct no consumer/pipeline, and leave journal, inbox, discovery and hold state unchanged with absent or stale discovery; a subsequent real drain dispatches unpaused under a fresh lifecycle); and `test_control_routing_lock_and_restart_races` (lock acquisition race, stale discovery/request, lifecycle replacement, no retargeting). `tests/test_daemon_composition.py` names `test_production_composes_one_pause_consumer` (shared seams and journal, graph construction has no decision or task); `test_live_drain_pause_blocks_all_offer_accounting` (real production root, fresh and retry offers, machine keep, snapshot and effects held, no false quiescence); `test_live_drain_resume_rechecks_selection_and_caps` (matching resume, changed eligibility/budget, exact retry/running order and free re-offers); and `test_control_lifecycle_cleanup_on_exit_and_handoff` (filesystem-seam trace proves live publication after lock acquisition, refresh after each durable decision, and `FileSystem.write` of `b"null\n"` before lock release on normal exit, failure, cancellation and before child launch; no raw unlink, a replacement publishes a fresh identity over retired discovery, and retired discovery cannot authorize a request).

  `tests/test_daemon_pause.py` replaces `test_dispatch_pause_boundary_is_dormant` with `test_dispatch_pause_boundary_is_active`, preserving active-work completion, cancellation cleanup and wrong-hold/stale/premature resume tests. The seeding ticket also fences `tests/test_control.py`, the predecessor's dormancy-pinning file under `19.L` ACTIVATION, and migrates only `test_control_inbox_is_dormant` to `test_control_inbox_is_active`; the registry fence is a floor. Verification runs `uv run pytest tests/test_daemon_pause.py tests/test_control_cli.py tests/test_daemon_composition.py tests/test_control.py tests/test_drain.py tests/test_cli.py tests/test_daemon_admission.py tests/test_daemon_config.py`; the last four are unchanged preservation suites. Exercise the real composed inbox and drain with disposable repositories, injected seams, scripted dispatch and asyncio barriers, never real-model calls or wall-clock waits. Each routing, identity, durability, accounting and cleanup assertion must fail when its production binding is deliberately removed or misordered.

AUTHORING CLOSURE: The sole addition beyond the registry floor is tests/test_control.py under 19.L ACTIVATION: migrate only test_control_inbox_is_dormant to test_control_inbox_is_active, including its production.control absence assertion and its calibrated run/drain no-consumption assertions. Preserve its other schema, durability, identity and ordering tests. The dispatch sibling creates tests/test_daemon_pause.py in this admission: it belongs in neither Context nor On-demand now; read its merged bytes before implementing and replace only test_dispatch_pause_boundary_is_dormant with test_dispatch_pause_boundary_is_active. tests/test_control_cli.py is also created, not embedded. All existing fenced paths are Context; authoring measurements fit 300,000-character headroom. The last four suites in the entry's Verification are unchanged preservation suites, neither fenced nor embedded.

Merged operations read at authoring: daemon.control_inbox(*, journal, lifecycle_id, holds, apply, files, read) constructs the existing ControlInbox; consume() and recover() remain its serial decision/fold operations. ControlProjection(lifecycle_id, pause_id, released_hold_ids, kill_requested) remains the desired-state projection. control.publish_request(state_dir, request, fs) validates and delegates to fs.publish; discovery uses fs.write, never another publication algorithm. The CLI currently has no pause/resume entries. Lockfile.acquire() determines the route and raises LockHeld on contention; release() ends ownership. Drain owns its lock across reconcile, intake, offers and terminals, then closes its journal and releases before self-upgrade child launch. Bind one consumer from those existing shared seams, with an injected async wakeup while paused. Read the merged dispatch-pause-boundary implementation before choosing its before_dispatch wiring; do not wrap only final dispatch after _select and cap accounting.

Closure greps across chupa/, eval/ and tests/ covered ControlInbox, control_inbox, ControlProjection, publish_request, DaemonAdmission, snapshot_dispatch, daemon_core, build_daemon_core, drain, pause/resume parser entries, public allowlists and old absence values. Direct factory callers are chupa/__main__.py and tests/test_daemon_composition.py; component callers in tests/test_daemon_admission.py and tests/test_daemon_config.py retain the optional construction seam. Existing drain callers in eval/shakeout/bench.py and tests/ retain their call shape. Keep existing control public operations and optional checkpoint callers valid; no mandatory constructor change earns another path. Do not change runner.compose_pipeline or activate queue holds here.

Prove real production routing and bindings through the merged production-composition harness, including calibrated deliberate removal or misordering. Ordinary graph construction performs no decisions or tasks. Preserve bootstrap inline admission, accounting, reconciliation, lock lifetime and terminals. Out: kill execution, admission/storm holds, background startup and continuous serve.


## Scope fence
- chupa/daemon.py
- chupa/control.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_daemon_pause.py
- tests/test_control_cli.py
- tests/test_daemon_composition.py
- tests/test_control.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_pause.py tests/test_control_cli.py tests/test_daemon_composition.py tests/test_control.py tests/test_drain.py tests/test_cli.py tests/test_daemon_admission.py tests/test_daemon_config.py` exits 0 with every own-entry named invariant test over real production routing and the shared drain consumer.
2. `tests/test_control_cli.py` proves exact live request identities, submitted output without a second writer/pipeline, idle lock acquisition and exact no-op messages, unavailable discovery refusals and restart/lock races.
3. `tests/test_daemon_composition.py` proves one shared consumer, no construction side effects, all offer accounting held, selection/caps re-read after matching release and atomic discovery retirement before exit/handoff.
4. `tests/test_daemon_pause.py` and `tests/test_control.py` migrate only the predecessor absence assertions and retain wrong-hold/stale/premature release, active completion, cancellation, schema and durability evidence.
5. `uv run pytest -q` exits 0 without removed or skipped tests; the last four entry Verification suites stay unchanged and bootstrap inline admission, accounting, reconciliation, lock lifetime and terminals are preserved.

## Verification
```
uv run pytest tests/test_daemon_pause.py tests/test_control_cli.py tests/test_daemon_composition.py tests/test_control.py tests/test_drain.py tests/test_cli.py tests/test_daemon_admission.py tests/test_daemon_config.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or incomplete contract for section 11.4 hardening if a needed fact is omitted or the criteria force an unearned path outside the fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
