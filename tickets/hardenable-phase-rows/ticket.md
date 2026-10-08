---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/specs.py
- tests/test_specs.py

## Plan contract
- section 11.4

## Goal / Why
`chupa/specs.py::hardenable_units` returns, for a ticket whose `## Plan contract` cites a phase unit `19.P<n>`, the entry unit of every non-exit row of that phase's registry as well, present or absent (section 11.4 HARDENABLE UNITS). A seeding ticket can then name a missing payload or lookahead unit in a `spec_gap` finding and the engine hardens it; today such a finding fails the reply schema because the missing unit is neither the ticket's own row nor citable.

## Scope in / Scope out
- In: `hardenable_units(plan, stem, plan_contract)` adds, for each cited `19.P<n>`, `19.P<n>.<row>` for every non-exit row of `BEGIN_REGISTRY_P<n>`, keeping its existing order (own unit, then cited units) followed by those phase rows, deduplicated.
- In: `tests/test_specs.py` adds `test_phase_citing_ticket_hardens_every_row_of_its_phase` (a ticket citing `19.P3` may name an absent `19.P3.<row>` in a `spec_gap` finding; a ticket not citing a phase unit still may not).
- Out: every other function, the reply schemas, and the routing.

## Scope fence
- chupa/specs.py
- tests/test_specs.py

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py` exits 0, including `test_phase_citing_ticket_hardens_every_row_of_its_phase`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_specs.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_specs.py -k test_phase_citing_ticket_hardens_every_row_of_its_phase
```
- carries: tests/test_specs.py

## Definition of rejected
Reject the branch if a ticket citing no phase unit gains any hardenable unit, if exit rows become hardenable, or if the regression test passes on the merge base.

## Time budget
- expected: 30m
- stuck: 90m
