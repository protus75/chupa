---
state: confirmed
source: seed
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
---

## Depends on
none

## Context
- tests/test_plan_lint.py

## Plan contract
- 19.L
- 19.P6
- 19.P6.core-drift-activation
- section 7
- section 8

## Goal / Why
`CHUPA_PLAN.md` states every fact `core-drift-activation` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.core-drift-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.core-drift-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Acceptance criterion 7 requires uv run pytest -q to pass after production activation. The mechanical conflict test passes on the untouched branch, but adding a passing core_drift gate to CHECK_GATES in memory fails its exact gate-sequence assertion. Plan unit 19.P6.core-drift-activation explicitly requires updating this assertion; the ticket excludes its file from the scope fence.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
