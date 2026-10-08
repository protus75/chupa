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
- 19.P3.checkpoint-push
- section 10

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.checkpoint-push` states every fact the `checkpoint-push` seed needs, so `phase3-continue-19` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.checkpoint-push` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.checkpoint-push

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.checkpoint-push` states, consistent with merged code: 19.P3.checkpoint-push requires failed pushes to enqueue through the supplied existing Box but never defines occurrence_id or its distinct-failure versus crash-replay semantics. The production storm_producer Box rejects the specified enqueue arguments with BoxError before writing a report. This reproduces on untouched merge-base 877406bfca38d533ae67bbf13e4fd4cebb04f216. Inventing this record identity violates the ticket's Records custody requirement.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.checkpoint-push`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
