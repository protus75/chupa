---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- tests/test_providers.py
- chupa/daemon.py
- chupa/tickets.py

## Plan contract
- section 6.11

## Goal / Why
`uv run pytest -q` is green on main again. `tests/test_providers.py::test_cli_failure_classifier_is_dormant` dispatches a bare `object()` as its ticket; since serve-activation's composition change, the production dispatch callback in `chupa/daemon.py` reads `ticket.stem`, so the fixture raises `AttributeError: 'object' object has no attribute 'stem'` and main's full suite is red, blocking every ticket whose Verification runs it.

## Scope in / Scope out
- In: the test's `run_ticket` fixture dispatches a real `Ticket` (built through `chupa.tickets.validate_ticket` from a minimal valid ticket text in the test's temporary repo) instead of `object()`; every assertion of `test_cli_failure_classifier_is_dormant` stays as it is.
- Out: any change to `chupa/` production code, and any other test.

## Scope fence
- tests/test_providers.py

## Acceptance criteria
1. `uv run pytest -q tests/test_providers.py` exits 0, including `test_cli_failure_classifier_is_dormant` with its assertions unchanged.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_providers.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_providers.py -k test_cli_failure_classifier_is_dormant
```
- carries: tests/test_providers.py

## Definition of rejected
Reject the branch if it changes production code, removes or weakens an assertion of `test_cli_failure_classifier_is_dormant`, or skips it.

## Time budget
- expected: 20m
- stuck: 60m
