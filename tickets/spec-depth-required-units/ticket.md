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
- chupa/stages.py
- tests/test_specs.py
- tests/test_seed_path.py

## Plan contract
- section 11.4

## Goal / Why
The seed path's mechanical SPEC DEPTH check in `chupa/stages.py` runs over each seed's REQUIRED units -- its own non-exit row's entry unit plus every registry entry unit it cites -- never the wider set a phase citation makes hardenable (section 11.4, 19.L). Today it calls `hardenable_units`, so a seed citing a phase unit (an exit seed citing the next phase) is snagged for every missing row of that phase, though only its own and cited units must exist.

## Scope in / Scope out
- In: `chupa/specs.py` gains `required_units(plan, stem, plan_contract)`: the own non-exit row's entry unit plus every cited registry entry unit, present or absent, in that order, deduplicated; `hardenable_units` returns `required_units` followed by its phase-row additions, unchanged in result.
- In: the mechanical SPEC DEPTH check in `chupa/stages.py` (the seed path, before grammar) iterates `required_units`; every other `hardenable_units` call site stays as it is.
- In: `tests/test_specs.py` adds `test_required_units_exclude_phase_rows`; `tests/test_seed_path.py` adds `test_phase_citing_seed_is_not_snagged_for_uncited_phase_rows` (a seed citing `19.P4` and two present P4 units, with other P4 rows missing, is not snagged by the mechanical check).
- Out: reply-schema validation, routing, and `hardenable_units`' result.

## Scope fence
- chupa/specs.py
- chupa/stages.py
- tests/test_specs.py
- tests/test_seed_path.py

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py tests/test_seed_path.py` exits 0, including `test_required_units_exclude_phase_rows` and `test_phase_citing_seed_is_not_snagged_for_uncited_phase_rows`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_specs.py tests/test_seed_path.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_seed_path.py -k test_phase_citing_seed_is_not_snagged_for_uncited_phase_rows
```
- carries: tests/test_seed_path.py

## Definition of rejected
Reject the branch if a seed's own or cited missing unit stops being snagged, if `hardenable_units`' result changes, or if the regression test passes on the merge base.

## Time budget
- expected: 30m
- stuck: 90m
