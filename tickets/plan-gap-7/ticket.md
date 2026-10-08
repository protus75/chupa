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
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase3-exit` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.watchdog-activation
- CHUPA_PLAN.md#19.P4.watchdog-detector

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.watchdog-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.watchdog-activation is also absent and fails both entry-depth validation and plan resolution. The required continuation cannot cite its activation contract or satisfy the seeder-role requirement without an out-of-fence plan edit.
3. `CHUPA_PLAN.md` unit `19.P4.watchdog-detector` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.watchdog-detector is absent: entry_unit_gap reports it missing and resolve_plan_contract refuses it. Section 13 requires phase4-continue to cite the entry units of the seeds it authors. Creating this governing contract requires an out-of-fence plan edit.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
