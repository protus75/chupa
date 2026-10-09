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
- 19.P5
- section 12
- section 13

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase5-continue-02` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P5.baseline-binding-reader
- CHUPA_PLAN.md#19.P5.status-projection

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P5.baseline-binding-reader` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> required_units identifies 19.P5.baseline-binding-reader as required for phase5-continue-03, but entry_unit_gap reports it missing; its required contract cannot resolve.
3. `CHUPA_PLAN.md` unit `19.P5.status-projection` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> required_units identifies 19.P5.status-projection as required for phase5-continue-03, but entry_unit_gap reports it missing and resolve_plan_contract finds zero matching headings.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
