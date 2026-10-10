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
- 19.P6
- 19.P6.bug-gate-grammar
- section 7
- section 13

## Goal / Why
`CHUPA_PLAN.md` states every fact `bug-gate-grammar` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.bug-gate-grammar

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.bug-gate-grammar` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Acceptance criteria 3 and 4 require rejecting missing-input failures while accepting defect failures from arbitrary argv commands. ProcessExec supplies only exit status and captured streams, which can be identical for both cases. The governing unit defines no defect-result protocol, and section 7 prohibits per-runner output parsing, so implementing this distinction requires inventing missing contract facts.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
