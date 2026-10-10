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
- 19.P6.supervised-merge-hold
- section 9
- section 12

## Goal / Why
`CHUPA_PLAN.md` states every fact `supervised-merge-hold` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.supervised-merge-hold

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.supervised-merge-hold` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The entry requires immutable candidate/base-keyed receipts and READY/confirmed for a confirmed green candidate, but does not specify receipt semantics when an existing HELD candidate is released without either identity changing. Effects.run replays the HELD completion for that same key. The entry must clarify whether unchanged-base confirmation and later GO reuse that receipt or require distinct READY evidence, including crash recovery.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
