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
> Activation must preserve the strict projected-wait >60-second spill rule, but 19.P3.thresh-runtime only defines a caller-supplied projected_wait_seconds input. The activation entry identifies neither its production source nor its calculation. The preserved LLMRequest and config contracts supply no projected duration; choosing zero, a timeout, or observed call durations would invent the governing selection policy.
3. `CHUPA_PLAN.md` unit `19.P4.provider-cooldown-failover` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Section 6.10 requires auth_error failover, but the activation entry defines candidate exclusion and release only for quota cooldowns and open breakers. The predecessor explicitly resets the breaker streak on auth_error. On untouched HEAD, an auth_error outcome leaves open_until null and the next admission selects the same primary. No rule defines how that credential failure excludes the candidate or how successful reauthentication restores it.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
