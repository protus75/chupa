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
- section 12
- section 13

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue-04` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.go-grade-machinery
- CHUPA_PLAN.md#19.P6.go-grade-run

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.go-grade-machinery` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The registry includes go-grade-machinery in admissions[6:], but its entry unit is absent: resolve_plan_contract matches zero headings and entry_unit_gap reports it missing. The required continuation must arrange its successor without inventing this governing contract.
3. `CHUPA_PLAN.md` unit `19.P6.go-grade-run` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The registry includes go-grade-run in admissions[6:], but its entry unit is absent: resolve_plan_contract matches zero headings and entry_unit_gap reports it missing. Its successor-chain citation cannot resolve before authoring.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
