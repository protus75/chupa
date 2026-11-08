---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- review-lock-only-for-intake

## Context
- chupa/lockfile.py
- chupa/__main__.py::_review
- chupa/tickets.py::intake
- tests/integration/test_review_command.py
- docs/how-chupa-works.md#2.1 Verbs

## Goal / Why
While a drain or serve holds the checkout lock, `./dev.py review X` refuses with `LockHeld`, even when `X` is already committed and needs no git write. Once `review-lock-only-for-intake` lands, review takes the checkout lock only to run intake, and journal appends have their own lock. After this change, reviewing a committed, unchanged ticket skips intake and never takes the checkout lock, so it runs next to a drain. A ticket file with uncommitted changes still needs intake, and it refuses with a fix the operator can follow.

## Scope in / Scope out
- In: `chupa/__main__.py::_review`. When `git status` shows no pending change under `tickets/<stem>/`, skip the lock and intake, and review `main:tickets/<stem>/ticket.md` as today. When there is a pending change, take the lock and run intake as today. If that raises `LockHeld`, refuse with this fix: wait for the running engine to commit the ticket (its intake does this), or stop it, then retry `review <stem>`.
- In: `tests/integration/test_review_command.py`. With a `Lockfile` held by the test, reviewing a committed, unchanged ticket returns 0 and journals its verdict. Reviewing a ticket with an uncommitted edit exits 2 without calling the model.
- In: `docs/how-chupa-works.md` section 2.1. The `review` row describes both cases.
- Out: running review as an engine control request; `triage`; drain and serve lock lifetimes; `confirm` and `reject`.

## Scope fence
- chupa/__main__.py
- tests/integration/test_review_command.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_review_command.py` passes. With the checkout lock held by another `Lockfile`, a committed, unchanged ticket's review exits 0 and journals one `requisition_verdict`, rather than raising `LockHeld`. An uncommitted edit exits 2 with `llm.requests == []`.
2. `./dev.py test tests/integration/test_drain.py tests/integration/test_requisition_gate.py` passes unchanged.

## Verification
```
./dev.py test tests/integration/test_review_command.py tests/integration/test_drain.py tests/integration/test_requisition_gate.py
```

## Definition of rejected
Reject the branch if review commits or writes any git state without holding the checkout lock, if it adds a control-request verb, or if it reviews working-tree text instead of the committed blob.

## Time budget
- expected: 25m
- stuck: 60m
