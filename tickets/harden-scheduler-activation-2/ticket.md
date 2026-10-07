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
- 19.P3.scheduler-activation

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.scheduler-activation` states every fact the `scheduler-activation` seed needs, so `phase3-continue-05` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.scheduler-activation` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.scheduler-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.scheduler-activation` states, consistent with merged code: 19.P3.scheduler-activation says the bind function in snapshot_dispatch(load, bind) 'receives the complete detached immutable snapshot and returns the existing Dispatch' using 'the existing production pipeline binding'. The existing binding is runner.Pipeline = Callable[[Checkout], Dispatch]. It takes a Checkout whose config field is typed Config, not ConfigSnapshot, and it builds ProviderLLM, Driver and StageContext from that field. runner.pipeline also calls asyncio.run(llm.preflight()) at line 81. Under snapshot_dispatch, bind runs inside DaemonAdmission's task in a running event loop, so asyncio.run raises RuntimeError there. With the default pipeline=runner.pipeline, the production root would therefore fail on its first admitted dispatch. The scripted-pipeline harness would never catch this. The entry unit leaves four facts unstated: how the snapshot is put into the Checkout (or its replacement) that consumers read, whether ConfigSnapshot is an accepted config type for runner, stages, driver and provider consumers, where provider preflight runs relative to admission, and which owner changes runner.pipeline/bind to do it. chupa/runner.py is in Context but not in the fence.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.scheduler-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
