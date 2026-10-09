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
- 19.P4.watchdog-activation
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `watchdog-activation` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.watchdog-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.watchdog-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.watchdog-activation requires expected/stuck budgets for every production call, including ticketless Author and triage. Those surfaces supply only AUTHOR_STUCK_S=900 and TRIAGE_STUCK_S=600, respectively; neither the cited contracts nor their inputs define an expected budget or its derivation. Detector.region requires that value to determine the expected-times-1.5 soft-warning boundary. Supplying one would invent governing behavior.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
