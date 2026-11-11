---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/runner.py::reject_ticket
- chupa/runner.py::_dead_dependents
- chupa/runner.py::_ticket_state
- tests/integration/test_reject_queue.py::test_reject_stamps_notifies_dependents_and_is_idempotent
- tests/regress_drain_deadline.py
- tests/unit/test_verdict_extension.py::Journal

## Goal / Why
`chupa reject <stem>` crashed with a `TicketInvalid` traceback and exit 1 on 2026-11-11 (evidence: `tickets/reject-survives-invalid-ticket/evidence/reject-crash.txt`). The reject had already been committed and journaled, but its dead-dependency sweep was skipped. The cause: `_dead_dependents` calls `parse_ticket` on every on-disk `tickets/*/ticket.md` whose frontmatter says `state: confirmed`. At that moment another session had an unfilled `chupa new` skeleton on disk. The skeleton carries `state: confirmed` but fails `parse_ticket`, and the exception escaped the verb. Any operator who rejects while a ticket is half-written in the shared checkout hits this.

After this change, `_dead_dependents` skips a ticket file that raises `TicketInvalid` and continues the sweep, so reject finishes, exits 0, and still notifies every valid dependent. An invalid ticket cannot run, so it needs no dead-dependency notice while it is invalid.

## Scope in / Scope out
- In: `chupa/runner.py`, `_dead_dependents` only: wrap the `parse_ticket(...)` call in `try` / `except TicketInvalid: continue`. Import `TicketInvalid` from `chupa.tickets` if it is not already imported there.
- In: `tests/integration/test_reject_queue.py`: add `test_reject_survives_invalid_confirmed_ticket`. Build it like `test_reject_stamps_notifies_dependents_and_is_idempotent`: commit `parent` and `child` (`child` depends on `parent`), queue `parent` with `_queued`, then write an uncommitted `tickets/aaa-wip/ticket.md` (the name sorts before `child`, so the sweep meets it first) whose frontmatter is `state: confirmed` and whose body fails `parse_ticket` (write the text literally in the test; do not build it from `chupa.tickets.template`, whose `state` line a sibling ticket changes). Run `main(["reject", "parent"], ...)` with the same `terminal=` answer as the existing test. Assert it returns 0, `child` has exactly one `dead_dependency` signal, and `tickets/aaa-wip/ticket.md` is byte-for-byte unchanged.
- In: `tests/unit/test_runner_dead_dependents.py` (new), because the `chupa/runner.py` coverage floor in `test-gate.toml` is measured from `tests/unit` only. Add `test_dead_dependents_skips_invalid_confirmed_ticket`. It awaits `runner._dead_dependents("parent", checkout)` on a `SimpleNamespace` checkout whose `repo` is a `tmp_path` tree holding `tickets/aaa-wip/ticket.md` (frontmatter `state: confirmed`, a body that fails `parse_ticket`) and a valid `tickets/child/ticket.md` that depends on `parent`. Its `journal` is an in-memory fake shaped like `Journal` in `tests/unit/test_verdict_extension.py`, holding a `parent` `state_transition` to `rejected`. Monkeypatch `chupa.daemon.storm_producer` to return a fake box whose `enqueue` records its calls. Assert `child` gets exactly one `dead_dependency` signal and the fake box gets exactly one `enqueue`.
- In: `tests/regress_reject_invalid_ticket.py` (new), the carried reproducer shaped like `tests/regress_drain_deadline.py`: it runs `pytest.main(["tests/integration/test_reject_queue.py", "-k", "survives_invalid", "-q", "-p", "no:cacheprovider"])` inside `contextlib.redirect_stdout(sys.stderr)` and prints exactly one JSON object `{"regression_result": ...}`: `pass` and exit 0 for pytest exit 0, `defect` and exit 1 for pytest exit 1, `error` and exit 2 otherwise.
- Out: `chupa/tickets.py` and the `chupa new` skeleton (the sibling ticket `new-skeleton-draft-state` owns that), other ticket scanners, `reject_ticket`'s commit and journal order, and any notice for invalid tickets.

## Scope fence
- chupa/runner.py
- tests/integration/test_reject_queue.py
- tests/unit/test_runner_dead_dependents.py
- tests/regress_reject_invalid_ticket.py

## Acceptance criteria
1. `uv run python tests/regress_reject_invalid_ticket.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head. On the base commit with the carried files overlaid it prints `defect`, because `reject` raises `TicketInvalid` instead of returning 0.
2. `./dev.py test tests/integration/test_reject_queue.py` passes `test_reject_survives_invalid_confirmed_ticket`, which asserts reject returns 0, not 1, and that `child` has exactly one `dead_dependency` signal, not zero. Because `aaa-wip` sorts before `child`, a fix that stops the sweep at the invalid file instead of skipping it leaves `child` with zero signals and fails.
3. `./dev.py test tests/unit/test_runner_dead_dependents.py` passes `test_dead_dependents_skips_invalid_confirmed_ticket`, which asserts `child` gets one `dead_dependency` signal, not zero, and that `_dead_dependents` returns instead of raising `TicketInvalid`; it runs the new `except` branch from `tests/unit`, so the `chupa/runner.py` coverage floor holds.
4. `./dev.py test tests/integration/test_reject_queue.py` still passes `test_reject_stamps_notifies_dependents_and_is_idempotent` unchanged.
5. `./dev.py test` exits 0.

## Verification
```
uv run python tests/regress_reject_invalid_ticket.py
./dev.py test tests/integration/test_reject_queue.py
./dev.py test tests/unit/test_runner_dead_dependents.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the handler catches anything broader than `TicketInvalid`;
- `chupa/tickets.py` changes;
- the reject's commit or journal order changes;
- the invalid ticket file is modified, stamped, or committed by reject;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 20m
- stuck: 45m

## Regression
```
uv run python tests/regress_reject_invalid_ticket.py
```
- carries: tests/regress_reject_invalid_ticket.py
- carries: tests/integration/test_reject_queue.py
