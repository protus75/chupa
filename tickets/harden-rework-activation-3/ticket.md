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
- 19.P3
- 19.P3.rework-activation

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.rework-activation` states every fact the `rework-activation` seed needs, so `phase3-continue-06` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.rework-activation` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.rework-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.rework-activation` states, consistent with merged code: The new terminal paragraphs cover only two paths: the diagnosis-driven path and the mechanical over-bound path. The conflict-handoff path is a third Rework entry, and Observable and test_production_applies_reviewed_rework_orders require it. MergeQueue.process returns a ConflictHandoff, not a StageResult, so runner.drive's terminal writer never sees it. The plan does not say who writes that run's producing `state_transition`. It also does not give its `to`/`stage`/`reason`, or whether diagnosis or a diagnosis/retry cap draw precedes Rework. It does not give the `dispatch`/`routed`/`rung` for update, split, escalate (with a rung or exhausted) and failed Rework/publication. Yet the unit requires that terminal to be written before a split original's separate `to: rejected` retirement, and it forbids Rework from emitting a terminal. Without these facts the implementer must invent the handoff-path terminal record and its writer.
3. `CHUPA_PLAN.md` unit `19.P3.rework-activation` states, consistent with merged code: The changed text says a successful split writes the producing terminal (e.g. `to: gate_failed`) and then a separate `to: rejected` retirement. Both are written under the held lock, inside the dispatch that drain._run_one awaits. It also says Rework does not turn the outcome into `rejected`, so drive returns the producing outcome. Merged drain._run_one requires the latest `state_transition` for the stem to equal the seam's return value ('the seam must journal the run's single terminal transition') and raises ValueError otherwise. A split under `drain` would therefore abort the drain. The plan does not say whether the seam returns `rejected` after retirement, or how drain's check identifies the producing terminal when a retirement follows it. Neither the ticket nor the unit names this drain invariant or a test for it.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.rework-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
