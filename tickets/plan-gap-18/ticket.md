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
- 19.P5
- section 13
- section 14

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase4-continue-05` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P5.retro-drain-invoker

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P5.retro-drain-invoker` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The exit must cite and validate the entry governing its next-phase core seed, but 19.P5.retro-drain-invoker is absent from the committed plan. resolve_plan_contract reports zero matching headings and entry_unit_gap reports the entry missing.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
