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

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase3-continue-22` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.daemon-soak
- CHUPA_PLAN.md#19.P3.daemon-soak-runner
- CHUPA_PLAN.md#19.P3.soak-run

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.daemon-soak` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> entry unit 19.P3.daemon-soak is missing
3. `CHUPA_PLAN.md` unit `19.P3.daemon-soak-runner` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> entry unit 19.P3.daemon-soak-runner is missing
4. `CHUPA_PLAN.md` unit `19.P3.soak-run` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> entry unit 19.P3.soak-run is missing

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
