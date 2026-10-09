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
- tests/test_stages.py

## On-demand
- specs/implement.md
- specs/requisition_review.md

## Plan contract
- section 11.4
- section 5

## Goal / Why
The Implement and requisition-review prompt specs tell the model which unit a `spec_gap` finding names using the full HARDENABLE set of section 11.4: the ticket's own non-exit registry entry unit, each registry entry unit its `## Plan contract` cites, and, for each cited phase unit `19.P<n>`, every non-exit row's entry unit of that phase; the unit named is the one missing or under-specified, never a unit that refers to it. Today `specs/implement.md` and `specs/requisition_review.md` still allow only own and cited units, so `phase6-continue` (citing `19.P6`) named `19.P6.fixture-host-scaffold` three times for the absent `19.P6.bug-gate-grammar` and `19.P6.report-inbox-triage`, and each hardener fenced to the wrong unit refused.

## Scope in / Scope out
- In: the `unit` rule in `specs/implement.md` and `specs/requisition_review.md` states the full HARDENABLE set above and that the unit named is the missing or under-specified one; each spec bumps its minor version.
- In: `tests/test_specs.py` adds `test_specs_name_every_hardenable_unit_kind` (both specs state the cited-phase-row case and the missing-unit rule) and its version pins in `test_spec_lint_accepts_the_implement_and_requisition_specs` follow the bumps; `tests/test_stages.py`'s run-record assertion follows the implement version.
- Out: `chupa/specs.py`, reply-schema validation, routing, and every other spec sentence.

## Scope fence
- specs/implement.md
- specs/requisition_review.md
- tests/test_specs.py
- tests/test_stages.py

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py tests/test_stages.py tests/test_requisition.py` exits 0, including `test_specs_name_every_hardenable_unit_kind`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_specs.py tests/test_stages.py tests/test_requisition.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_specs.py -k test_specs_name_every_hardenable_unit_kind
```
- carries: tests/test_specs.py

## Definition of rejected
Reject the branch if either spec still restricts `unit` to own and cited units, if any other spec sentence changes, if production code changes, or if the regression test passes on the merge base.

## Time budget
- expected: 20m
- stuck: 60m
