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
- 19.P3.admission-holds-activation

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.admission-holds-activation` states every fact the `admission-holds-activation` seed needs, so `phase3-continue-09` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.admission-holds-activation` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.admission-holds-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.admission-holds-activation` states, consistent with merged code: 19.P3.admission-holds-activation requires one CLI-owned inbox supplied to both factories without fallback, but the pipeline is built before drain constructs its consumer and no shared carrier exists. The entry omits that carrier while requiring tests/test_drain.py to remain unchanged despite its direct drain, bind, and positional Checkout callers. These facts were verified against base HEAD 4cd71ddf38e55b5b404bccaaf007264e122d285e.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.admission-holds-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
