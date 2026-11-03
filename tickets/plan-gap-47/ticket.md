---
state: rejected
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
- 19.P7
- 19.P7.host-mechanical-check
- section 7

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase7-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P7.host-mechanical-check

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P7.host-mechanical-check` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P7.host-mechanical-check requires accepting declared host mechanical bypass codes, but omits how chupa/triage.py::attribute_escape must preserve historical frontmatter validation and names no test for that consumer. The ticket explicitly requires a spec-gap stop when this necessary triage behavior or test is absent.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
