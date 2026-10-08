---
priority: P0
kind: feature
source: human
state: confirmed
---

## Depends on
- spec-gap-unit-detection

## Context
- chupa/stages.py
- chupa/specs.py
- tests/test_seed_path.py

## Plan contract
- 19.L

## Goal / Why
A seed authored by a seeding ticket never carries plan-unit text. Beside the SPEC DEPTH check, the seed path snags a seed whose body outside `## Plan contract` contains, verbatim after whitespace normalization, any line of 60 or more characters from a plan unit the seed cites. The snag is `kind: authoring_error` with the paved road "cite the unit in `## Plan contract`; never copy its text".

Why: the plan's 19.L SPEC DEPTH COPY REFUSAL makes the never-copy rule mechanical. A seed that copies unit text goes stale when the unit is hardened, and each hardening then forced a hand regeneration of the seed plus a resync of its seeding test's pins. The rule is prose-only today, so nothing enforces it.

## Scope in / Scope out
- In: `chupa/stages.py` `_review_one` gains a mechanical pre-check that runs after the SPEC DEPTH check and before `validate_ticket`. It resolves the seed's raw `## Plan contract` ids through `chupa.specs.resolve_plan_contract` against main's plan, skipping any id that does not resolve, since grammar reports those. It collapses each resolved line's whitespace to single spaces and strips it. It snags the seed with mechanical `unit text copied` when any such line of at least 60 characters appears in the seed's text outside its `## Plan contract` section after the same normalization. The finding's message names the cited id and quotes the first 80 characters of the copied line.
- Out: engine-composed hardening tickets, which do not pass through `_review_one`; human and box tickets; Plan-contract rendering.

## Scope fence
- chupa/stages.py
- tests/test_seed_path.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seed_path.py` exits 0. It includes `test_seed_copying_a_cited_unit_line_is_snagged_without_a_review_call`: a seed whose Goal repeats a 60-plus-character line of its cited `19.L` gets a `requisition_review` snag with `kind: authoring_error`, the paved road text above, and mechanical `unit text copied`, and makes no `requisition_review` call. It includes `test_short_or_uncited_overlap_is_not_a_copy`: a 59-character shared line, or a line copied from a plan unit the seed does not cite, is reviewed normally.
2. `uv run pytest -q tests/test_stages.py tests/test_requisition.py` exits 0 unchanged.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_stages.py tests/test_requisition.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if the check reads a seed's prose for anything except the copy comparison, if it applies to tickets other than seeds under seeding review, or if a copied seed reaches a `requisition_review` call.

## Time budget
- expected: 30m
- stuck: 90m
