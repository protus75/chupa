---
priority: P1
kind: bug
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/triage.py::_settle_pass
- chupa/author.py::recover_retro_ticket
- chupa/box.py::Box.record_recurrence
- tests/integration/test_triage.py::test_reopened_message_bypasses_its_tombstone
- tests/unit/test_verdict_extension.py
- tests/regress_drain_deadline.py

## Goal / Why
`Box.record_recurrence` (`chupa/box.py`) clears a reopened message's verdict and resolution and sets it back to pending. Triage then records a fresh author verdict and calls `author()`. Several awaited steps run before `author()` journals `author_invoked`. A drain kill, SIGHUP or reload in that window leaves a recorded author verdict with no new `author_invoked` signal. On resume, the guard in `_settle_pass` (`chupa/triage.py`, the `invoked = any(... "author_invoked" ...)` line) searches the whole journal with no round boundary. It finds the first authoring round's signal and calls `failure_declined`. That writes and commits `declined-<id>`. The damage lasts: on any later recurrence reopen, `_settle_pass` removes only the `tombstone-<id>` record, not `declined-<id>`, so the registry lookup resolves the message as declined again and Author never runs. A recurring defect after a merged fix, which is what `retro-finding-recurrence` exists to re-author, is then silently dropped. The merged ticket added the reopen boundary at the two sites in `chupa/author.py` (`record_retro_ticket`, `recover_retro_ticket`) but missed this guard.

After this change, the `author_invoked` check counts only signals after the latest `retro-recurrence/<id>/` `EFFECT_INTENT` whose body has `reopened: true`, the same boundary rule `chupa/author.py` uses. With no such intent the check is unchanged.

## Scope in / Scope out
- In: `chupa/triage.py`. In `_settle_pass`, compute the boundary index over `checkout.journal.read()` exactly as `recover_retro_ticket` does (the max index of an `EFFECT_INTENT` whose key starts with `retro-recurrence/{message.id}/` and whose body `reopened` is `True`, default -1). Count only `author_invoked` signals for this message at a later index. Read the journal once and reuse it for both the boundary and the signal scan.
- In: `tests/unit/test_triage_author_boundary.py` (new). Unit tests that drive `_settle_pass` directly (the hard `unit` coverage gate measures `chupa/triage.py` from `tests/unit` only). Use a fake checkout whose `journal.read()` returns in-memory events (shape them like the Journal fake in `tests/unit/test_verdict_extension.py`) and counts its calls, and a fake box whose `pending()` yields one message with a current-version author verdict. Monkeypatch `recover_retro_ticket` (return None), `read_registry` (return []), `author` and `failure_declined` with AsyncMocks. Tests: `test_reopened_stale_author_invoked_calls_author` (the only `author_invoked` precedes the reopened intent: assert `author` is awaited and `failure_declined` is not), `test_author_invoked_after_boundary_declines` (the `author_invoked` follows the intent: assert `failure_declined` is awaited and `author` is not), and `test_guard_reads_journal_once` (assert `journal.read()` was called exactly once on the guard path).
- In: `tests/integration/test_triage.py`. Add `test_reopened_author_verdict_with_stale_author_invoked_calls_author`. It builds a pending message with a recorded author verdict (current spec version) and an `author_invoked` signal for it appended to the journal before a `retro-recurrence/<id>/...` intent with `reopened: true`. It runs triage and asserts `triage.author` is called once and `declined-<id>` is not written.
- In: `tests/regress_triage_author_invoked_boundary.py` (new), the carried reproducer shaped like `tests/regress_drain_deadline.py`. It calls `pytest.main(["tests/integration/test_triage.py", "-k", "stale_author_invoked", "-q", "-p", "no:cacheprovider"])` inside `contextlib.redirect_stdout(sys.stderr)`, so pytest's report stays off stdout. It then prints exactly one JSON object with only the `regression_result` key on stdout: `defect` and exit 1 when pytest exits 1, `pass` and exit 0 when pytest exits 0, `error` and exit 2 for any other pytest exit.
- Out: the `declined-<id>` record cleanup on reopen, changes to `chupa/author.py` or `chupa/box.py`, moving the `author_invoked` append earlier, and other crash-window hardening.

## Scope fence
- chupa/triage.py
- tests/unit/test_triage_author_boundary.py
- tests/integration/test_triage.py
- tests/regress_triage_author_invoked_boundary.py

## Acceptance criteria
1. `uv run python tests/regress_triage_author_invoked_boundary.py` prints `{"regression_result": "pass"}` on stdout alone and exits 0 on the branch head. It prints `defect`, not `pass`, when a reopened message whose only `author_invoked` precedes the boundary is declined.
2. `./dev.py test tests/unit/test_triage_author_boundary.py` passes `test_reopened_stale_author_invoked_calls_author`, which asserts `author` is awaited and `failure_declined` is not. A guard that ignores the boundary fails it.
3. `./dev.py test tests/unit/test_triage_author_boundary.py` passes `test_author_invoked_after_boundary_declines`, which asserts `failure_declined` is awaited. A guard that ignores all `author_invoked` signals fails it.
4. `./dev.py test tests/unit/test_triage_author_boundary.py` passes `test_guard_reads_journal_once`, which asserts `journal.read()` is called exactly once. An implementation that reads the journal twice fails it.
5. `./dev.py test tests/integration/test_triage.py` passes `test_reopened_author_verdict_with_stale_author_invoked_calls_author`, which asserts `author` runs and no `declined-<id>` record exists.
6. `./dev.py test` exits 0.

## Verification
```
uv run python tests/regress_triage_author_invoked_boundary.py
./dev.py test tests/unit/test_triage_author_boundary.py
./dev.py test tests/integration/test_triage.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- an `author_invoked` signal after the latest reopen boundary no longer leads to `failure_declined`;
- the boundary is derived from anything other than the `retro-recurrence/<id>/` intent with `reopened: true`;
- `chupa/author.py` or `chupa/box.py` changes;
- the reproducer prints `pass` on the merge base, or prints anything but one JSON object on stdout.

## Time budget
- expected: 30m
- stuck: 75m

## Regression
```
uv run python tests/regress_triage_author_invoked_boundary.py
```
- carries: tests/regress_triage_author_invoked_boundary.py
- carries: tests/integration/test_triage.py
