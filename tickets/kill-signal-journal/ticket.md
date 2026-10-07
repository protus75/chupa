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

## Context
- chupa/control.py
- chupa/daemon.py

## Plan contract
- 19.I
- 19.P3.kill-signal-journal
- section 20

## Goal / Why
Dormant kill-signal journaling. Build only the explicit dormant boundary over the merged owners and seams.

## Scope in / Scope out
- **Owner:** `chupa/control.py` owns kill validation, durable decisions, and their journal-derived projection through the existing `ControlInbox`. `chupa/daemon.py` owns the dormant boundary supplied with the lock-holder's journal, lifecycle identity, and idempotent application callback. No new module or second journal writer is introduced; reuse the predecessor inbox and fold.
- **Records:** Reuse `<state_dir>/control/inbox/<request_id>.json` with the closed shape `{request_id: str, lifecycle_id: str, verb: pause | resume | kill, hold_id: str | null}`. A kill carries `verb: kill`, null `hold_id`, a nonempty target lifecycle id, and a nonempty request id restricted to ASCII letters, digits, underscore, and hyphen matching its filename. Publication uses the existing durable no-overwrite filesystem seam, writes only the request file, and requires a fresh request id if its destination exists. It never creates a lifecycle or writes a journal signal. Unknown or duplicate keys, wrong types, invalid identities, and non-null kill holds are rejected with the valid request shape as the paved road; unsafe filenames and private temporaries are never consumed.

  Reuse `CONTROL_DECISION = "control_decision"`, owned by `chupa/control.py`, written solely by the lock-holding consumer as `EventType.SIGNAL`, null ticket/key, body `{kind: control_decision, request_id: str, lifecycle_id: str | null, verb: pause | resume | kill | null, hold_id: str | null, decision: accepted | stale | rejected, reason: str}`. A valid current-lifecycle kill retains its exact identities, `verb: kill`, null hold, and an accepted decision. A valid prior-lifecycle kill is stale, mutates nothing, and directs the caller to read the current lifecycle and submit a new request. Malformed input is rejected with the safe filename identity, null unvalidated fields, and the valid shape without echoing arbitrary input. Consume serially in deterministic filename order; append/fsync the decision before application. An append failure leaves the request undecided and invokes no callback.

  The journal's request-id decision fold is the exactly-once authority; retain decided files as inert input, never a processed marker. Repeated scans, changed bytes under a decided id, and reconstruction cannot append another decision. Current-lifecycle accepted kills fold into the existing in-memory `ControlProjection.kill_requested: bool`, initially false and latched true; pause/resume cannot clear it. Old-lifecycle decisions never latch a new lifecycle. A crash after durable acceptance but before application reconstructs the idempotent desired projection without another decision or repeated external action. Introduce no event type, signal constant, configuration, ticket frontmatter, cap draw, terminal, or applied record. The later `kill-cli-activation` owns recording application only after executor unwind; acceptance alone never proves completed execution.
- **Observable:** Explicitly exercise this dormant boundary through injected journal, clock, filesystem, identity, and projection seams. A matching kill's durable decision is visible before its callback; stale/rejected kills never change the projection. Duplicate consumption and crash recovery preserve one decision and an idempotent latch. Preserve predecessor pause/resume and hold behavior. Construction is behaviorally dormant under `19.I`: real CLI run/drain and the production-composition harness never bind kill application or invoke kill execution. Executor abort, worker cancellation, failure suppression, dispatch stopping, concurrent control polling, and the CLI kill verb remain the named later kill/activation rows' obligations. No production task is started by construction; `kill-cli-activation` later migrates this row's dormancy assertion.
- **Tests:** `tests/test_kill_signal_journal.py` adds `test_kill_decision_precedes_projection` (callback reads the exact durable signal, append failure prevents mutation), `test_kill_identity_and_shape_fail_closed` (current/stale lifecycles, malformed requests, null hold requirement, exact decision bodies and paved roads), `test_kill_decision_is_once` (retained files, repeated scans, altered decided bytes, reconstructed consumer), `test_kill_decision_crash_recovery` (before append and after acceptance/before application, one decision, idempotent latch, prior-lifecycle decisions cannot retarget), `test_kill_projection_stays_latched` (pause/resume preserve the latch and their own semantics), and `test_kill_signal_journal_is_dormant` (calibrated raising kill-application probes over real CLI run/drain and the production graph, no kill signal, execution, or extra task). Exercise the real inbox through `chupa/daemon.py`'s supplied boundary, never a test-only decision implementation. Verify with `uv run pytest tests/test_kill_signal_journal.py tests/test_control.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py`; unchanged predecessor suites preserve publication, folding, control dormancy, and production composition. Use disposable directories and injected seams, never real-model calls or wall-clock waits. Applying before the durable decision, duplicating a decision, or applying a stale kill must fail its named test.

AUTHORING CLOSURE: The registry floor needs no additions under 19.L rules 2-5. Existing fenced owners are Context; the new test is created and belongs in neither Context nor On-demand. Preservation suites run unchanged in Verification only, neither fenced nor embedded. No production signature or constructor changes; no public-operation allowlist or old production absence assertion needs migration. Historical seeding tests stay unchanged.

Authoring rg across chupa/, eval/ and tests/ covered abort_current, Driver construction/run/race/_kill, timeout ownership, optional review waits, cancellation handling, ControlInbox, ControlProjection.kill_requested, control_inbox, PauseConsumer, DaemonTasks, public-operation allowlists, not hasattr and production absence assertions. Existing LLM.abort_current callers are providers/fakes and Driver._kill. Driver.race also serves chupa/requisition.py; keep its signature and behavior. Driver construction and run signatures remain unchanged, so their callers need no edits. The timeout path and external abort must share cleanup ownership. No allowlist pins Driver or daemon operations. ControlInbox already validates and folds kill; reuse it rather than duplicating decisions. Existing tests/test_control.py kill assertions preserve projection-only behavior and altered decided-file inertia; no assertion flip is earned. The merged production harness is tests/test_daemon_composition.py (CoreRig and LiveDrain); read it as a read-only reference and exercise its real graph from the new suite without changing or embedding this preservation suite. chupa.daemon is already reachable, so import absence is not dormancy evidence.

Calibrate raising probes: deliberately supplied kill-application/external-abort wiring must trip its probe, while real CLI run/drain and ordinary production composition leave it untouched. Preserve the invocation's shared admission/dispatch control consumer, independent holds, and bootstrap inline admission. Out: worker stop, failure suppression, concurrent polling, CLI kill activation, background startup, serve wiring, replacement control implementation or abort path, new modules, records, constants, config and frontmatter.

## Scope fence
- chupa/control.py
- chupa/daemon.py
- tests/test_kill_signal_journal.py

## Acceptance criteria
1. `uv run pytest tests/test_kill_signal_journal.py tests/test_control.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py` exits 0 with every own-entry named invariant test, calibrated raising dormancy probes, and preserved predecessor behavior.
2. `tests/test_kill_signal_journal.py` proves the complete Owner, Records, Observable and Tests contract above, including exact custody, ordering, identity, crash/cancellation edge behavior and behavioral dormancy through real CLI run/drain and production composition.
3. `uv run pytest -q` exits 0 without removed or skipped tests; no production kill wiring, worker control, background task or serve activation is introduced.

## Verification
```
uv run pytest tests/test_kill_signal_journal.py tests/test_control.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or contradictory entry unit for section 11.4 hardening if a needed fact is omitted or a criterion forces an unearned path outside the fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
