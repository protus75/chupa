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
- 19.P4
- section 6
- section 15

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase4-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.provider-cooldown-failover

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.provider-cooldown-failover` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> At committed HEAD 9288276c229f58fe9260a8488aa460c502f2541d, provider-cooldown-failover exists in the Phase 4 registry but its required entry unit is absent. The successor must cite that next-admission authoring contract; resolve_plan_contract rejects 19.P4.provider-cooldown-failover because it matches zero headings. This is a required-citation resolution failure, not preemptive validation of later payload criteria.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
