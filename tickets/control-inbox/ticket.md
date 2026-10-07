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
- background-consumers

## Context
- chupa/daemon.py
- chupa/seams.py
- chupa/journal.py
- tests/test_effects.py

## Plan contract
- 19.I
- 19.P3.control-inbox
- section 20

## Goal / Why
Dormant crash-safe inbox: identity-bound, exactly once, decision journaled before mutation; publication through a tested durable no-overwrite filesystem-seam operation.

## Scope in / Scope out
- **Owner:** The new `chupa/control.py` owns typed control requests, publication, validation, journal-derived consumption, and lifecycle/hold identity matching. `chupa/daemon.py` owns the dormant consumer boundary supplied with the lock-holder's journal, lifecycle identity, current hold identities, and an injected application callback; it never opens a second journal writer. `chupa/seams.py` owns the filesystem publication primitive, in both `FileSystem` and `LocalFileSystem`. Use the existing `Journal.append` write-ahead fsync and `EventType.SIGNAL`, not a second decision store. Construction introduces no CLI routing, dispatch checkpoint, kill executor, worker task, polling loop, or production lifecycle startup; those belong to the named later activation rows.
- **Records:** Requests live under `<state_dir>/control/inbox/<request_id>.json`. A request is a closed JSON object `{request_id: str, lifecycle_id: str, verb: pause | resume | kill, hold_id: str | null}`. Request and lifecycle ids are nonempty opaque identities; request ids used as filenames are restricted to ASCII letters, digits, underscore, and hyphen, with no path separators. Filename and body identity must agree. The publisher supplies a fresh request id and the target lifecycle id; publication never generates or retargets an engine lifecycle. Each running engine's owner supplies a restart-unique lifecycle id, distinct from a checkout id, PID, ticket stem, or reused lockfile instance id. `pause` and `kill` require null `hold_id`; `resume` requires the exact nonempty identity of the hold it releases. Each pause or admission/storm hold has its own identity, never merely its kind. A resume without a hold identity is refused with the paved road to read the current hold and submit a new request. These files have no ticket frontmatter and change no ticket schema or configuration.

  Publication is a new filesystem-seam operation `publish(path, data: bytes) -> None`: create a private unique temporary file in the destination directory, write all bytes and fsync it, atomically publish the complete file without overwriting an existing destination, and fsync the destination directory before reporting success. Concurrent publishers cannot share a temporary filename. An existing destination raises `FileExistsError`, leaves its bytes unchanged, and requires a new request id; any interrupted private temporary file is never a consumable request. The seam owns directory creation and its durability, temporary cleanup, and every raw filesystem operation needed for publication. Existing `write` and `replace` semantics and callers remain unchanged; overwrite-capable `write` is not an inbox publication path. The CLI-side publisher writes only the request file, never a journal event, decision, or governed state.

  `chupa/control.py` alone owns `CONTROL_DECISION = "control_decision"`. The lock-holding consumer is its sole writer: one `EventType.SIGNAL` with envelope `ticket: null`, `key: null`, body `{kind: control_decision, request_id: str, lifecycle_id: str | null, verb: pause | resume | kill | null, hold_id: str | null, decision: accepted | stale | rejected, reason: str}`. A valid request retains its exact identities and verb; malformed input uses the safe filename identity and nulls for unvalidated fields, with a nonempty diagnostic reason. Unknown keys, wrong types, missing fields, unknown verbs, invalid identities, and incompatible hold fields are rejected before application; diagnostics give the valid request shape instead of echoing arbitrary input bytes. A valid request targeting another lifecycle, or a resume targeting an absent/different hold, is stale and mutates nothing. Accepted decisions name the matching lifecycle and, for resume, matching hold. Decisions are keyed logically by request id in the journal fold, not by ticket/run Effect keys. Reusing an already-decided request id never creates another decision or application, even with changed request bytes.

  Consume complete request files serially in deterministic filename order; journal append order is the decision order. Journal the decision durably before invoking any application callback, then derive consumed identities from that journal on every reconstruction. Keep decided request files as inert input; deletion or a separate processed marker is not the exactly-once authority. If journaling fails, application does not run and the request remains undecided. Recovery after a durable accepted decision and before application reconstructs the current lifecycle's governed projection from accepted decisions in journal order; it does not append another decision. Applying that projection must be idempotent, so repeated folds/reconstruction cannot repeat an external action. Old-lifecycle decisions remain recorded but cannot apply to a new lifecycle. An arbitrary callback with unreplayable side effects is not an exactly-once implementation; later kill construction owns abort completion and its applied record. Construction exercises application through an injected idempotent projection, without activating those later effects.
- **Observable:** Explicit publication and consumption exercise the real dormant component through injected filesystem, clock, journal, identity, and application seams. Every request gets at most one durable decision; accepted requests affect only their bound lifecycle and hold, after that decision is visible. Repeated scans, reconstructed consumers, duplicated publication, and interruption before/after publication or decision cannot lose a successfully published undecided request, expose partial JSON, overwrite a request, duplicate a decision, or release a later hold. Accepted pause decisions establish a pause whose identity is that request id; only a matching resume releases it. Fold decisions in journal order so the latest accepted pause/resume governs that projection; a previously filed resume never releases a subsequently created hold. A stale kill never invokes the application seam. This construction does not spend dispatch/retry accounting or implement kill execution.

  Dormancy under `19.I` is behavioral: production graph construction and CLI `run`/`drain` neither construct nor consume the inbox or publish a lifecycle. Test the production composition harness once it exists, otherwise the real CLI composition root with its injectable pipeline seam. Raising construction/consumption probes must fail under deliberate wiring and remain untouched by ordinary production calls. Do not require `chupa.daemon` import absence, since scheduler activation makes that module reachable. `pause-resume-activation`, the kill rows, admission/storm hold activations, and `serve-activation` own their production bindings and migrate only the dormancy assertions they invalidate. The pre-daemon direct locked control behavior remains outside this construction.
- **Tests:** `tests/test_control.py` names `test_request_shape_and_identity_fail_closed` (every schema/type/verb/filename refusal and paved road); `test_publication_is_durable_and_never_overwrites` (real disposable filesystem, file/directory fsync ordering, existing destination and concurrent publishers, complete visibility, preserved bytes); `test_publication_crash_points` (failure before file fsync, before/after atomic publication, and before directory fsync, ignored private temporaries, no success before durability); `test_publisher_never_writes_journal` (request-only publication); `test_decision_precedes_application` (callback reads its durable decision, journal failure prevents mutation); `test_request_is_decided_once` (repeated scans, consumer reconstruction, duplicate id with altered bytes, retained files); `test_decision_crash_reconstructs_projection` (crash before append and after durable acceptance/before application, no duplicate decision or external action); `test_lifecycle_identity_never_retargets` (restart-unique lifecycle, stale pause/resume/kill and prior decisions mutate nothing); `test_resume_matches_only_its_hold` (absent hold, premature resume, replaced hold, matching pause/admission/storm identities); `test_latest_accepted_pause_resume_wins` (ordered journal fold and repeated recovery); and `test_control_inbox_is_dormant` (production harness or real CLI `run`/`drain`, calibrated probes, no lifecycle, decision, control mutation, or consumer task). Verification runs `uv run pytest tests/test_control.py tests/test_cli.py tests/test_drain.py`, plus `tests/test_daemon_composition.py` unchanged once merged. All invariants are exercised through the production dormant component and seams, with disposable directories and synchronization barriers, never real-model calls or wall-clock waits.

CALLER CLOSURE: CONTRADICTED TESTS/CALLER CLOSURE: test_fakes_satisfy_seam_protocols asserts isinstance(FakeFS(), FileSystem); adding publish to the runtime protocol requires the fake to supply that operation while preserving write/replace behavior. Add publish only to that fake as needed for its existing runtime protocol assertion; retain all existing Effects invariants.

CONSTRUCTION BOUNDARY: Preserve bootstrap run/drain inline admission, accounting, reconciliation, lock lifetime and terminals. Leave chupa/__main__.py and tests/test_daemon_composition.py unedited. Reuse the existing production composition harness from the unchanged preservation suite to calibrate raising construction/run or consumption probes: prove deliberate wiring raises and ordinary graph construction plus CLI run/drain never touches the new boundary. Daemon import absence is no longer evidence after scheduler activation. Do not activate background task startup, CLI control routing, dispatch pause, kill, admission/storm holds or serve.

## Scope fence
- chupa/control.py
- chupa/daemon.py
- chupa/seams.py
- tests/test_control.py
- tests/test_effects.py

## Acceptance criteria
1. `uv run pytest tests/test_control.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py tests/test_effects.py` exits 0 and proves every named own-entry invariant, exact record custody and behavioral dormancy through the real dormant component and calibrated production probes.
2. `uv run pytest tests/test_control.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py tests/test_effects.py` preserves bootstrap run/drain inline admission, accounting, reconciliation, lock lifetime and terminals with all preservation suites unchanged.
3. `uv run pytest -q` exits 0 with no test removed or skipped and no production activation.

## Verification
```
uv run pytest tests/test_control.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py tests/test_effects.py
uv run pytest -q
```

## Definition of rejected
Stop with premise_failed if a criterion forces a path outside the fence or the governing entry omits a needed fact; name the missing contract for section 11.4 hardening. Refuse invented records, replacement graphs and production behavior outside this admission.

## Time budget
- expected: 60m
- stuck: 90m
