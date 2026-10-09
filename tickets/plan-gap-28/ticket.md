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
> The Scope requires phase6-continue-03 to carry position 3 and admissions[3:], which starts with [bug-gate-grammar, report-inbox-triage]. It also requires running required_units and entry_unit_gap on every required non-exit entry, including the successor's next-admission entries. Under section 13's seeding-role grammar, phase6-continue-03 must cite the entry units of the seeds it authors, 19.P6.bug-gate-grammar and 19.P6.report-inbox-triage, and the grammar gate refuses an unresolvable Plan contract id. CHUPA_PLAN.md has no heading for either unit: the 19.P6 entry units stop at fixture-host-scaffold. The successor therefore cannot be authored grammar-valid. 19.P6.fixture-host-scaffold, the cited unit that bug-gate-grammar's registry row depends on, says phase6-continue-02 checks SPEC DEPTH on every entry unit its seeds need, but the plan does not state the Owner, Records, Observable or Tests of the successor's next-admission rows. By the ticket's own instruction, Implement deterministically returns premise_failed.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
