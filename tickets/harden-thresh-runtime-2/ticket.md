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
- 19.P3.thresh-runtime
- section 6

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.thresh-runtime` states every fact the `thresh-runtime` seed needs, so `phase3-continue-03` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.thresh-runtime` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.thresh-runtime

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.thresh-runtime` states, consistent with merged code: 19.P3.thresh-runtime defines spill only for a FULL primary (alternate free and closed, primary's supplied projected wait > 60s) and a refusal only when NO candidate is available. It never states what admission does when the first route candidate's breaker is OPEN but a later candidate's is closed. Admission could skip to that candidate, which overlaps the ordered failure-driven failover reserved for 19.P4. It could also refuse, which contradicts 'refuse only when no candidate is available'. If the closed later candidate is at its own cap, it is unstated whether the caller waits FIFO there and which projected wait governs, since the caller supplies one duration for the primary only. test_spill_requires_available_candidate_and_wait_over_sixty_seconds and test_open_route_refuses_without_effect_or_cap_draw cannot pin behavior the spec never states.
3. `CHUPA_PLAN.md` unit `19.P3.thresh-runtime` states, consistent with merged code: The Observable requires 'Recheck availability when a waiter reaches the head' but never states the outcome when the recheck fails, i.e. the waited-on provider's breaker opened while the call was queued. The waiter could be refused with the typed pre-call refusal, re-run selection over the route (possibly spilling), or keep waiting until the deadline. The provider_cap_wait record's closed disposition vocabulary (admitted | cancelled) has no value for this exit either, so the record shape for this path is also missing.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.thresh-runtime`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
