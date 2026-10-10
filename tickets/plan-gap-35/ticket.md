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
- section 10
- section 14

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue-02` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.escape-column

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.escape-column` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Authoring a buildable phase6-continue-03 requires governing its creation of phase6-continue-04 for the escape-column admission. On the untouched committed HEAD, entry_unit_gap reports 19.P6.escape-column missing and resolve_plan_contract finds zero headings. Its Owner, Records, Observable and Tests cannot be supplied without inventing plan facts.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
