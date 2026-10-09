---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/tickets.py
- tests/test_tickets.py

## Plan contract
- section 13.3
- section 9.7

## Goal / Why
Ticket grammar refuses a `## Time budget` whose `stuck` does not exceed its `expected` (section 13.3), with a paved road naming both values. That rule is the plan's guard against an expected==stuck authoring mistake (section 9.7); today `chupa/tickets.py` accepts any two positive integers, so the guard does not exist.

## Scope in / Scope out
- In: the `## Time budget` grammar check in `chupa/tickets.py` adds a finding when `stuck <= expected`, paved road `set stuck greater than expected (the stage deadline is the stuck budget)`; `tests/test_tickets.py` adds `test_time_budget_stuck_must_exceed_expected` (equal and lower stuck refused, greater accepted).
- Out: the stage deadline, the watchdog, and every other grammar rule.

## Scope fence
- chupa/tickets.py
- tests/test_tickets.py

## Acceptance criteria
1. `uv run pytest -q tests/test_tickets.py` exits 0, including `test_time_budget_stuck_must_exceed_expected`.
2. `uv run pytest -q` exits 0, so every committed ticket still passes intake under the rule.

## Verification
```
uv run pytest -q tests/test_tickets.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_tickets.py -k test_time_budget_stuck_must_exceed_expected
```
- carries: tests/test_tickets.py

## Definition of rejected
Reject the branch if a ticket with `stuck` equal to or below `expected` passes grammar, if any other grammar rule changes, or if the regression test passes on the merge base.

## Time budget
- expected: 20m
- stuck: 60m
