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
`CHUPA_PLAN.md` states every fact `phase6-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.core-drift-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.core-drift-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> On main, CLAUDE.md and AGENTS.md contain no chupa:core markers, and chupa's config routes both claude and codex. classify_core therefore returns `missing` for both files. This ticket ships core_drift as a hard gate in Check and in the inline and queued merge rerun. It explicitly leaves migration and docs out, and it fences neither conduct file. Phase 6 Deliverables call chupa's own CLAUDE.md/AGENTS.md 'the first case' of first adoption, but no registry row owns rendering and committing them. 19.P6.core-drift-activation also omits this fact. As a result, from the next drain onward, every ticket on this repo (starting with migrate-config, admitted in the same admission) fails core_drift before main moves. The only way out is an unplanned operator `chupa core` plus a hand commit of a section-17 render target. That is a hold with no planned release.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
