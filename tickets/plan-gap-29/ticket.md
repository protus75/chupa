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
- 19.P6
- 19.P6.fixture-host-scaffold

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.fixture-host-scaffold

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.fixture-host-scaffold` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P6.fixture-host-scaffold requires phase6-continue-02 to depth-check every entry its seeds need. Its required successor phase6-continue-03 must cite 19.P6.bug-gate-grammar and 19.P6.report-inbox-triage for admission position 3, but both entry headings are absent from committed HEAD. Authoring the continuation would require fabricating governing facts or editing the plan outside this ticket's fence.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
