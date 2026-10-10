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
- 19.P6
- section 9
- section 12

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue-03` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.supervised-merge-hold

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.supervised-merge-hold` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> phase6-continue-04 must author escape-column and its successor phase6-continue-05, which governs the supervised-merge-hold admission. That required entry unit is absent: resolve_plan_contract finds zero headings and entry_unit_gap reports it missing. A buildable successor contract cannot be authored under the ticket's prohibition on fabrication.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
