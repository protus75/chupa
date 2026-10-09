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
- 19.P6.core-drift-activation
- section 7
- section 8

## Goal / Why
`CHUPA_PLAN.md` states every fact `core-drift-activation` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.core-drift-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.core-drift-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Acceptance criterion 7 requires the full suite to pass with core_drift hard. This imported repository constructor introduces both routed CLIs but commits only CLAUDE.md, causing test_outbox_only_admission_records_null_commit_and_retires to fail. Repairing that constructor requires an edit outside the scope fence.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
