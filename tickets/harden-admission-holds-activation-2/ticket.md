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
2. `CHUPA_PLAN.md` unit `19.P3.admission-holds-activation` states, consistent with merged code: The ticket requires `<state_dir>/control/active.json` `{lifecycle_id, hold_id}` to show the current releasable admission hold identity. But `write_active` (chupa/control.py, Context only, not fenced) writes `hold_id` from `ControlProjection.pause_id` alone, and the CLI `_control` resume submits only that one discovered hold. The ticket also requires that a pause and an admission hold can be live at the same time and are released independently. The plan contract (19.P3.admission-holds-activation) does not say which identity goes in the single `hold_id` slot when both are live, or how the slot is derived from the queue's hold. Without that, publishing the admission identity needs either an edit to control.py, which is outside the fence, or a precedence rule invented by daemon.py.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.admission-holds-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
