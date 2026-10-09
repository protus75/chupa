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
- 19.P5
- section 18

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase5-continue-02` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P5.retro-doctor-cli

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P5.retro-doctor-cli` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The ticket says phase5-continue-04 requires 19.P5.retro-doctor-cli and its row citation, and that this entry must be validated before any file is authored. The P5 registry has a retro-doctor-cli row (cite [18], VERBS contract), but CHUPA_PLAN.md has no '### 19.P5.retro-doctor-cli' heading. The P5 entry units stop at 19.P5.baseline-binding-reader. So entry_unit_gap(plan, '19.P5.retro-doctor-cli') returns 'entry unit 19.P5.retro-doctor-cli is missing'. The successor's Plan contract also cannot cite that unit, because the grammar gate refuses unresolvable ids. Following its own Scope and Definition of rejected, Implement must return premise_failed before seed creation, so acceptance criteria 1 and 2 cannot be met. The plan does not state the facts this unit needs: an Owner for chupa/doctor.py and the retro verb composition; Records for the retro/doctor outputs, exit codes and lock interaction; an Observable; and named Tests such as the doctor check order and retro no-merge, success and no-commit paths.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
