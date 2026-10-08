---
state: confirmed
source: seed
priority: P1
kind: chore
agent_tier: high
agent_effort: high
---

## Depends on
none

## Context
- tests/test_plan_lint.py

## Plan contract
- 19.L
- 19.P3
- section 10

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase3-continue-22` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.outbox-only-admission

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.outbox-only-admission` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Live admissions[23] requires 19.P3.outbox-only-admission, but its entry unit is absent. Mandatory lookahead validation fails, preventing authoring phase3-continue-23 without inventing its contract.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
