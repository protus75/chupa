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
- 19.P4
- 19.P4.watchdog-detector
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase4-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.watchdog-detector

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.watchdog-detector` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.watchdog-detector sets the threshold as spend strictly above SPIRAL_SPEND_MULTIPLIER times 'the serving row's per-call basis (metered cost when available, otherwise its declared estimate)', but it never says which metered cost is the basis. For a cost-reporting provider with no `limits.est_cost_per_call_usd` (ClaudeAdapter.reports_cost=True; config.py allows the estimate to be None), the only metered cost is the cumulative `total_cost_usd` on the terminal `result` event. If the basis is that same call's cost, the threshold is circular: spend can never exceed 3x itself within one call. Across re-prompts with retained state, the basis is still unnamed: first call, latest call, a running mean, or something else. test_spend_metering_and_threshold must assert exact equality and strict crossing, so the implementer would have to invent this fact.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
