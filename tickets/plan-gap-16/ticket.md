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
- 19.P4
- 19.P4.provider-cooldown-failover
- section 6
- section 15

## Goal / Why
`CHUPA_PLAN.md` states every fact `provider-cooldown-failover` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.provider-cooldown-failover

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.provider-cooldown-failover` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.provider-cooldown-failover requires a pre-dispatch infra_error transition carrying provider_drought without a running offer. The existing auditor reports "terminal 'infra_error' has no open run" for that exact record, conflicting with section 15's green-auditor requirement for fake-driven production evidence. Repair requires changing the unfenced auditor.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
