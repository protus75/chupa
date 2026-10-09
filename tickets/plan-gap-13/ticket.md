---
state: rejected
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
- 19.P4
- section 6

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase4-continue-02` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.reliability-battery

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.reliability-battery` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The reliability-battery registry row exists, but resolve_plan_contract cannot resolve 19.P4.reliability-battery. Authoring phase4-continue-03 requires this citation, so the ticket cannot be completed without inventing governing facts or editing the read-only plan.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
