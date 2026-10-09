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
- section 15

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase5-exit` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.fixture-host-scaffold
- CHUPA_PLAN.md#19.P6.host-contract-doc

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.fixture-host-scaffold` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The second next-admission row, fixture-host-scaffold, has no `### 19.P6.fixture-host-scaffold` entry unit either. The successor needs this unit to pass depth validation and to cite it, so it fails in the same way.
3. `CHUPA_PLAN.md` unit `19.P6.host-contract-doc` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The ticket requires required_units/entry_unit_gap to pass for the successor's next-admission entries, and requires phase6-continue-02 to cite them. The plan has only four 19.P6 entry headings: core-renderer, core-drift-classifier, core-drift-activation and migrate-config. There is no `### 19.P6.host-contract-doc`, so entry_unit_gap returns 'entry unit 19.P6.host-contract-doc is missing'. The successor cannot cite it either, because the grammar gate refuses an id that does not resolve. Authoring would end in premise_failed every time.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
