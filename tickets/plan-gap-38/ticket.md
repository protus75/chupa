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
- 19.P6.bug-gate-grammar
- section 7
- section 13

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue-03` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.bug-gate-grammar

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.bug-gate-grammar` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> Sections 7.1 (rung 4) and 7.2 make the merge stage the single writer to main and require it to re-run the hard gate set itself. DEFAULT_GATE_SEVERITY marks bug_evidence hard at merge. Merge re-gating has two paths: chupa/merge.py:346-352 runs CHECK_GATES, and chupa/mergequeue.py:271-274 runs the same tuple during integration. Neither reads Check's checks.json reports; SeedSafetyGate reads only its seeds. The unit names Check as the only executor and writer of the bug_evidence report and gives the merge-time re-run no owner. If the gate joins CHECK_GATES, merge does re-run it, but the exact gate-code list asserted by tests/test_mergequeue.py::test_strategy_resolution_still_regates changes, and that file is outside the fence. If the gate is added only inside check(), a kind: bug branch merges without bug_evidence ever being re-gated. Neither choice is buildable from the spec as it stands.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
