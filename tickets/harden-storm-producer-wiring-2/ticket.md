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
- 19.P3.storm-producer-wiring
- section 12

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.storm-producer-wiring` states every fact the `storm-producer-wiring` seed needs, so `phase3-continue-16` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.storm-producer-wiring` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.storm-producer-wiring

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.storm-producer-wiring` states, consistent with merged code: 19.P3.storm-producer-wiring delegates production occurrence_id supply to storm-notification-activation, but that activation unit specifies only storm-report/<trip_id>. It omits the closed production arrival-site list and replay-stable id recipes for runner harvest/dependency failures, stages second problems/failure reports, flake quarantine, and bootstrap ingest. Those caller files also lack explicit fence treatment. The gap exists on the base commit.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.storm-producer-wiring`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
