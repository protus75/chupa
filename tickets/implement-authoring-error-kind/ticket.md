---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- tests/test_specs.py
- tests/test_stages.py

## On-demand
- specs/implement.md

## Plan contract
- section 5
- section 11.4
- 19.L

## Goal / Why
The Implement prompt spec defines both premise kinds as section 5 does: `spec_gap` when a hardenable unit is missing, lacks a SPEC DEPTH part, or omits or contradicts a fact the work needs; `authoring_error` when the ticket contradicts stated spec or merged code or is malformed, including a `## Scope fence` missing a path the criteria force (19.L rule 2's fence wall). Today `specs/implement.md` defines only `spec_gap`, so fence walls arrive as `spec_gap` against units that already state the closure: `core-drift-activation` drew six hardening rounds, two ending `already_satisfied`, for two unfenced test files.

## Scope in / Scope out
- In: `specs/implement.md`'s premise-finding paragraph defines `authoring_error` as above, names the fence wall as its case, and keeps `unit: null` for it; the `spec_gap` sentences are unchanged; the spec bumps its minor version.
- In: `tests/test_specs.py` adds `test_implement_spec_defines_both_premise_kinds` (the spec states the `authoring_error` definition and the fence-wall case); its version pin in `test_spec_lint_accepts_the_implement_and_requisition_specs` and the run-record assertion in `tests/test_stages.py` follow the bump.
- Out: production code, reply-schema validation, routing, and every other spec.

## Scope fence
- specs/implement.md
- tests/test_specs.py
- tests/test_stages.py

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py tests/test_stages.py tests/test_requisition.py` exits 0, including `test_implement_spec_defines_both_premise_kinds`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_specs.py tests/test_stages.py tests/test_requisition.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_specs.py -k test_implement_spec_defines_both_premise_kinds
```
- carries: tests/test_specs.py

## Definition of rejected
Reject the branch if the `spec_gap` or `unit` sentences change, if any other spec changes, if production code changes, or if the regression test passes on the merge base.

## Time budget
- expected: 20m
- stuck: 60m
