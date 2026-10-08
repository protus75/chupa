---
state: confirmed
source: seed
priority: P1
kind: chore
agent_tier: high
agent_effort: high
---

## Depends on
none

## Context
- tests/test_plan_lint.py

## Plan contract
- 19.L
- 19.P3
- 19.P3.worker-recovery-disposition
- section 6
- section 15

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase3-continue-21` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.worker-recovery-disposition

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.worker-recovery-disposition` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Merged `chupa/journal.py` (lines 36-44) lists `SIGNAL_NAMES` without `recovery_alert`, and its append seam rejects any name outside that set (lines 128-130). So the `{kind: recovery_alert, ...}` signal that `19.P3.worker-recovery-disposition` requires `reconcile.py` to append can only work if `journal.py` is edited. The payload's registry floor is only `chupa/reconcile.py` and `tests/test_reconcile.py`. The entry unit's Owner bullet keeps `run_seq`, `TERMINAL_STATES`, the envelope and durable append with `journal.py`, but never mentions registering the signal name or adding `journal.py` to the fence. Its Tests bullet earns only `tests/test_restart_timers.py`. 19.L allows a seeding ticket to widen a fence only for paths found by mechanical rules 2-5; any other widening is a plan edit. Sibling entry units that needed a seam-owner addition say so explicitly (for example `19.P3.merge-queue` and `19.P3.serve-merge-admission`: 'Under 19.L ... closure, the implementing seed adds ...'). This unit has no such statement, so the ticket's own claim that `chupa/journal.py` is earned is seeding-time invention. Without that edit, the seed's criteria cannot be met inside its floor fence.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
