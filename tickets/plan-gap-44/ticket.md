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
- 19.P7
- 19.P7.host-mechanical-check
- section 7
- section 7.3

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase7-core` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P7.host-mechanical-check

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P7.host-mechanical-check` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> host-mechanical-check requires citations 7 and 7.3. resolve_plan_contract rejects that combination because a section cannot be cited with its own subsection, while ticket grammar requires both. Confirmed on unchanged base ef1e00a692782410c7d9a62e5ee57c370b75e42f.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
