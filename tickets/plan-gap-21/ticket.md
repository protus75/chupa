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
- section 14

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase5-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P5.scorecard-reporting

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P5.scorecard-reporting` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The successor must cite 19.P5.scorecard-reporting. required_units returns that entry, but the committed base plan contains no matching heading, so its Owner, Records, Observable and Tests cannot be validated as required before either seed is written.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
