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
- section 6
- section 13
- section 15
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase3-continue-27` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.notify-transport
- CHUPA_PLAN.md#19.P4.watchdog-event-stream

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.notify-transport` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.notify-transport is absent on committed HEAD c59c6310d16fccb829dea75dad7bf32da5ffd093: entry_unit_gap reports missing and resolve_plan_contract finds zero headings. Adding the required contract is outside this ticket's scope fence.
3. `CHUPA_PLAN.md` unit `19.P4.watchdog-event-stream` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.watchdog-event-stream is absent on committed HEAD c59c6310d16fccb829dea75dad7bf32da5ffd093: entry_unit_gap reports missing and resolve_plan_contract finds zero headings. The terminal cannot author its required next-phase core without inventing governing facts.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
