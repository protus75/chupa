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
- 19.P3.serve-activation
- section 18
- section 20

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.serve-activation` states every fact the `serve-activation` seed needs, so `serve-activation` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.serve-activation` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.serve-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.serve-activation` states, consistent with merged code: 19.P3.serve-activation requires one shared Journal and reuse of the existing triage/Author path. triage_pass internally constructs Driver.from_config, which creates a separate Journal and Effects owner, and exposes no binding seam for the caller to supply checkout.journal. Satisfying this custody requirement requires an edit outside the earned fence; copying triage or replacing its writer through runtime monkeypatching would violate the governing contract.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.serve-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
