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
- 19.P3.serve-activation
- section 18
- section 20

## Goal / Why
`CHUPA_PLAN.md` states every fact `serve-activation` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.serve-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.serve-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The unit requires scheduler-side storm selection governed by section 12, which suppresses the emitting stage and reserves whole-ticket selection for bootstrap. However, Scheduler.dispatch_next holds its slot through the entire ticket callback, DaemonAdmission does likewise, and chupa/stages.py::run_stages directly invokes Implement, Check and Review without a stage-selection or suspension seam. The unit does not specify how a held stage retains its producing run while freeing selection for unrelated work. Adding that seam requires the unfenced chupa/stages.py; filtering entire tickets or copying its orchestration would bypass the governing contract.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
