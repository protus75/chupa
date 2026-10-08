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
- 19.P3
- section 9

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.serve-merge-admission` states every fact the `serve-merge-admission` seed needs, so `phase3-continue-19` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.serve-merge-admission` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.serve-merge-admission

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.serve-merge-admission` states, consistent with merged code: entry unit 19.P3.serve-merge-admission is missing

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.serve-merge-admission`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
