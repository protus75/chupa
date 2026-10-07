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
2. `CHUPA_PLAN.md` unit `19.P3.rework-activation` states, consistent with merged code: 19.P3.rework-activation removes the `dispatch: reject_queue` / `routed: reject_queue` marker for diagnosis `split` while budget remains, and it activates the 11.3 mechanical over-bound route. It also requires the producing run terminal to be written before the separate retirement transition. Neither it nor sections 11.2-11.4 says what that terminal `state_transition` body records for a Rework-routed run. Today runner.drive only writes `dispatch` values of retry, escalate, reject_queue or spec_gap_hold, and the over-bound terminal carries no `dispatch` at all. Four facts are missing: (1) the `dispatch` value, if any, when Rework returns `split` and publication succeeds, and when it returns `update`; (2) whether a Rework `escalate` reply maps to the existing `dispatch: escalate` + `rung` from `next_rung`, and what an exhausted ladder routes to on the over-bound path, which promises no cap draw; (3) whether a failed Rework or failed publication terminal carries `routed: reject_queue` or what other paved routing; (4) whether the next dispatch of an updated original is a drain re-offer that draws a `retry` cap_consumed unit, or a 'fresh dispatch' that draws none. The unit also forbids any new constant, so a value such as `dispatch: rework` cannot be invented. These facts are asserted by test_split_dispatches_reviewed_rework ('one terminal after application, no split Reject marker'), test_rework_update_reenters_on_fresh_content, and test_render_over_bound_dispatches_rework_without_diagnosis.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.rework-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
