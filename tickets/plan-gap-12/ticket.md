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
- 19.P4
- 19.P4.watchdog-activation
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `watchdog-activation` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P4.watchdog-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P4.watchdog-activation` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P4.watchdog-activation requires ticket-owned expected budgets to come from the ticket, derives expected budgets only for ticketless calls, and preserves existing LLM effect identities. Mandatory migration targets eval/harness.py:185 and eval/diagnose.py:175 pass non-null synthetic ticket identities (baseline-<fixture> and diagnose-eval-<case>). All 22 baseline fixture tickets and all 12 diagnosis fixture tickets lack Time budget sections; their callers supply only hard budgets. The entry supplies no expected-budget policy for these synthetic identities. Inventing expected values violates the governing rule; converting them to surface-owned ticketless calls changes existing effect keys; adding fixture budgets requires unfenced edits.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
