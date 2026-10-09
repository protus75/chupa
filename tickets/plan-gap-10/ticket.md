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
- 19.P4
- 19.P4.watchdog-detector
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `watchdog-detector` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.watchdog-detector

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.watchdog-detector` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The detector entry requires section 9.7's expected-to-stuck floor and a test proving it, but section 9.7 names no formula or minimum. Existing Driver code uses the supplied stuck budget directly. Choosing a floor would invent governing behavior.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
