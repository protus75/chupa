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
- 19.P6.go-grade-machinery
- section 12
- section 13

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue-06` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.go-grade-machinery

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.go-grade-machinery` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P6.go-grade-machinery Records says to raise MIN_DEFECTS to 50 and MIN_CLEAN to 15 and to keep each review fixture as a directory of ticket.md, diff.patch and expected.json. load_fixtures refuses any committed set below those floors. The committed set has 22 fixtures (18 planted, 4 clean), so this one diff would add at least 43 fixture directories, which is 129 files and several thousand inserted lines. DiffBudgetGate (chupa/stages.py:43-44, section 7) caps a diff at 30 files and 1,500 inserted lines, and section 7 says a fixture corpus must be one closed envelope file per case. The alternative also fails: raising the floors without growing the corpus breaks tests/test_watchdog_activation.py:239, which calls harness.load_fixtures() on the committed set and is one of the ticket's own Verification commands. The ticket author cannot fix this, because the unit both requires the shape and assigns the corpus growth to this seed.
3. `CHUPA_PLAN.md` unit `19.P6.go-grade-machinery` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The unit says that no paid baseline run is needed to build the machinery and that all tests use scripted providers. Yet it also requires this seed to commit 43 or more new fixtures, each recording an author identity whose (provider, model) differs from the reviewer's. The only fixture-authoring path is the paid `eval.harness author` command. The unit does not say who authors the new fixtures, by what process, or under which recorded identity. Without that, the Implement agent would hand-write fixtures and stamp an author identity on them that no recorded authoring step backs.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
