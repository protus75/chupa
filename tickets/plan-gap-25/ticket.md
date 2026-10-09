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
- section 7
- section 8
- section 15

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase5-exit` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.core-drift-activation
- CHUPA_PLAN.md#19.P6.migrate-config

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.core-drift-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> At untouched base 26d0838bba011c38e616765a351c5db55f7b9136, phase6-continue must cite and depth-check 19.P6.core-drift-activation, but entry_unit_gap reports it missing and resolve_plan_contract finds zero headings.
3. `CHUPA_PLAN.md` unit `19.P6.migrate-config` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> At the same untouched base, phase6-continue must cite and depth-check 19.P6.migrate-config, but entry_unit_gap reports it missing and resolve_plan_contract finds zero headings; repairing the plan is outside this ticket’s fence.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
