## Outcome

premise_failed

## Surprises / judgment calls

On the untouched branch, tests/test_policy.py passes; temporarily moving specs into chupa/specs makes test_standing_go_uses_the_table_and_each_override_drafts fail because it still reads ROOT / "specs". The move was restored and no changes were committed.

## Dead ends

Checked the repository’s spec-path consumers; preserving the old directory would violate the acceptance criteria and rejection conditions.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.3

## Predicted vs actual

none

