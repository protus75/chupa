---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- phase2-exit

## Context
- chupa/__main__.py

## Plan contract
- 19.L
- 19.P3
- section 9

## Goal / Why
Build the dormant single-flight scheduler and watcher re-prioritization from the first Phase 3 registry row. `chupa/scheduler.py` owns scheduling, `chupa/watcher.py` owns ticket-change observation, and `tests/test_scheduler.py` owns their direct and dormancy proofs. Production activation belongs to the later `scheduler-activation` row.

## Scope in / Scope out
- In: one ticket at a time dispatches through the scheduler; changes observed by the watcher cause pending work to be considered again in priority and authoring-age order, without preempting an active ticket. Exercise both components directly with injected seams.
- In: the watcher debounces edits, keeps an existing ticket's last known good sort position when an edit cannot parse, excludes a new invalid ticket, and journals the parse failure.
- In: `tests/test_scheduler.py` proves the transitive `chupa.*` import closure rooted at `chupa/__main__.py` excludes both new modules, recognizing `import chupa.x` and `from chupa import x`; the test must fail when either module becomes reachable.
- Out: production CLI or daemon wiring, and any later Phase 3 row.

## Scope fence
- chupa/scheduler.py
- chupa/watcher.py
- tests/test_scheduler.py

## Acceptance criteria
1. `tests/test_scheduler.py` proves no two dispatched tickets execute at once, a new P0 waits for an active ticket, and a watcher change reorders pending tickets by priority, first authoring event, then stem.
2. `tests/test_scheduler.py` proves a half-written edit is debounced, a malformed existing edit keeps its last known good sort position, a malformed new ticket stays ineligible, and each parse failure is journaled.
3. `tests/test_scheduler.py` proves the transitive import closure from `chupa/__main__.py` excludes `chupa.scheduler` and `chupa.watcher` and detects either import idiom when made reachable.
4. `uv run pytest -q` exits 0 without removing or skipping a test.

## Verification
```
uv run pytest -q tests/test_scheduler.py
uv run pytest -q
```

## Definition of rejected
Reject if either module is reachable from the production CLI, if single-flight or watcher re-prioritization has no discriminating test, or if the diff leaves the fence.

## Time budget
- expected: 60m
- stuck: 90m
