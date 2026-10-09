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
- section 7
- section 13
- section 12

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.bug-gate-grammar
- CHUPA_PLAN.md#19.P6.report-inbox-triage

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.bug-gate-grammar` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Required successor phase6-continue-03 must cite 19.P6.bug-gate-grammar, but its entry heading is absent from committed HEAD. required_units includes it, entry_unit_gap reports it missing, and resolve_plan_contract finds zero headings. Authoring the required continuation would fabricate governing facts or require an out-of-fence plan edit.
3. `CHUPA_PLAN.md` unit `19.P6.report-inbox-triage` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Required successor phase6-continue-03 must cite 19.P6.report-inbox-triage, but its entry heading is absent from committed HEAD. required_units includes it, entry_unit_gap reports it missing, and resolve_plan_contract finds zero headings. The required successor depth proof cannot pass without inventing its contract.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
