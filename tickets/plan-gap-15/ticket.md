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

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase4-continue-02` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.reliability-run

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.reliability-run` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Scope in requires resolve_plan_contract to resolve 19.P4.reliability-run, the successor phase4-continue-04's required next-admission citation. Under 13.3 and 19.L, a seeding ticket cites the entry units of the seeds it authors, and the 19.P4.reliability-battery Owner bullet sets the same pattern for the predecessor's successor seed. CHUPA_PLAN.md has entry units only up to `### 19.P4.reliability-battery` and has no `### 19.P4.reliability-run`. resolve_plan_contract raises PlanContractError on an id that matches zero headings, and entry_unit_gap returns 'entry unit 19.P4.reliability-run is missing'. The successor seed therefore cannot carry a resolvable Plan contract, and the plan does not state the reliability-run row's Owner, Records, Observable or Tests (its OUTBOX run-lane admission, producer custody and report destination).

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
