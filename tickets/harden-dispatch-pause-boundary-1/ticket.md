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
- 19.P3
- section 20

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.dispatch-pause-boundary` states every fact the `dispatch-pause-boundary` seed needs, so `phase3-continue-05` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.dispatch-pause-boundary` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.dispatch-pause-boundary

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.dispatch-pause-boundary` states, consistent with merged code: entry unit 19.P3.dispatch-pause-boundary is missing

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.dispatch-pause-boundary`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
