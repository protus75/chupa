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
- section 8
- section 15

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase5-continue-05` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.core-drift-classifier
- CHUPA_PLAN.md#19.P6.core-renderer

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.core-drift-classifier` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Required entry unit 19.P6.core-drift-classifier is missing on the untouched base commit; resolve_plan_contract finds zero headings, so its Owner, Records, Observable and Tests cannot be read.
3. `CHUPA_PLAN.md` unit `19.P6.core-renderer` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Required entry unit 19.P6.core-renderer is missing on the untouched base commit; resolve_plan_contract finds zero headings, so its Owner, Records, Observable and Tests cannot be read.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
