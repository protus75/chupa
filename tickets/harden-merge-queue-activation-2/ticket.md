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
- 19.P3.merge-queue-activation

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.merge-queue-activation` states every fact the `merge-queue-activation` seed needs, so `phase3-continue-06` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.merge-queue-activation` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.merge-queue-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.merge-queue-activation` states, consistent with merged code: Owner/Observable require `compose_pipeline` to build `MergeQueue(ctx, *, escalate)` with the 'supplied escalation consumer', reached through `runner.bind`, and the test `test_production_pipeline_composes_merge_queue` asserts that injected consumer. Neither the plan unit 19.P3.merge-queue-activation nor the ticket names where it comes from. `bind(checkout, llm)` and `pipeline(checkout)` may not change signature, `Checkout` has no escalation field, and section 13 defers notify transport to the 19.P4 notify-transport stem: until then escalations exist only as journaled signals, which `MergeQueue._signal` already writes. The missing facts are: which consumer production passes (for example a no-op, since the journal already carries the record), who builds it (bind, the CLI root, or a new Checkout field), and whether `compose_pipeline` takes it as a required keyword. Registry row admission-holds-activation (plan line 1760) later says every direct `compose_pipeline` caller supplies a shared inbox, so this ticket's choice has to fit that.
3. `CHUPA_PLAN.md` unit `19.P3.merge-queue-activation` states, consistent with merged code: Observable says the production harness 'obtains the queue from this binding' and Owner says the factory 'exposes that queue to its consumers'. But `bind` returns the `Dispatch` lambda `Callable[[Ticket], Awaitable[str]]` with its contract preserved, and `build_daemon_core`/`prepare` hand out only that callable. The spec never names how the composed queue becomes observable without a second test-only queue: an attribute on the returned callable, a return value from compose_pipeline captured by wrapping `merge.compose_pipeline`, or a StageContext/driver slot. Implementers would have to invent this, and the three daemon-composition tests depend on it.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.merge-queue-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
