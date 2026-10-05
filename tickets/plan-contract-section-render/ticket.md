---
state: confirmed
source: seed
priority: P0
kind: bug
agent_tier: high
agent_effort: medium
---

## Depends on
none

## Context
- chupa/specs.py
- chupa/tickets.py
- tests/test_specs.py
- tests/test_stages.py

## Plan contract
- 19.L
- 19.P2

## Goal / Why
The Implement render of a ticket whose `## Plan contract` cites a numeric section (for example `section 11`) resolves that section's plan bytes into the prompt. Today it raises `PlanContractError`.

Why: `validate_ticket` stores each `Plan contract` bullet in `Ticket.plan_contract` in its CANONICAL form (`section 11` becomes `11`, the form `plan_id` returns). `implement_stage` in `chupa/stages.py` hands those canonical ids to `resolve_plan_contract`, which re-parses each one as a bullet and refuses `'11'` as "not a plan id". Unit ids (`19.L`, `19.P2`) survive the round trip, so nothing caught it. Every Phase 2 seed cites the owning sections it builds on, so each one would die at its first Implement render. The drain would stop on the first seed rather than run the spine. This is a code defect, not the plan's: section 13 says the renderer resolves the cited ids verbatim.

## Scope in / Scope out
- In: `resolve_plan_contract` in `chupa/specs.py` consumes CANONICAL ids: the form `plan_id` returns and `Ticket.plan_contract` carries. It still refuses an unresolvable id, section 22, and an id matching more or fewer than one heading.
- In: every caller that holds bullet text canonicalizes through `plan_id` first. That means `validate_ticket` in `chupa/tickets.py`, and the resolver tests in `tests/test_specs.py`, which change only their input form, never what they assert.
- In: a regression test in `tests/test_stages.py` named with `plan_contract`. It drives the production Implement stage on a ticket citing a numeric section and asserts the rendered prompt carries that section's heading.
- Out: any change to the `Plan contract` bullet grammar (a bare `11` bullet stays refused at intake), to the `Ticket` field, or to `chupa/stages.py`.

## Scope fence
- chupa/specs.py
- chupa/tickets.py
- tests/test_specs.py
- tests/test_stages.py

## Acceptance criteria
1. `uv run pytest -q tests/test_stages.py -k plan_contract` passes on the branch. On the merge base with the branch's `tests/test_stages.py` overlaid, it fails with `PlanContractError`.
2. The `python -c` command in `## Verification` exits 0: resolving `Ticket.plan_contract` of a ticket citing `section 11` returns text starting with `## 11.`.
3. A `## Plan contract` bullet written as a bare `11` is still refused by `validate_ticket` (an existing or added assertion in `tests/test_specs.py` or `tests/test_stages.py`).
4. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_stages.py -k plan_contract
uv run python -c "from pathlib import Path; from chupa.specs import resolve_plan_contract, plan_id; assert resolve_plan_contract(Path('CHUPA_PLAN.md').read_text(), [plan_id('section 11')]).startswith('## 11.')"
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_stages.py -k plan_contract
```
- carries: tests/test_stages.py

## Definition of rejected
Reject the branch if any of these hold:
- The fix loosens the bullet grammar.
- The resolver accepts two input forms (a dual path).
- A resolver assertion in `tests/test_specs.py` is weakened.
- The diff touches a file outside the fence.

## Time budget
- expected: 20m
- stuck: 40m
