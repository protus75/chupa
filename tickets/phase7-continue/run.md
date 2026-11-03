## Outcome

premise_failed

## Surprises / judgment calls

The new snapshot’s 7 tests and plan lint’s 29 tests pass. Both seeds remain unchanged; tests/test_seeded_phase7_01.py remains uncommitted.

## Dead ends

Stopped after full-suite verification returned 2 failed and 3874 passed; historical fixtures were preserved.

## Second problems filed

- box-000298-e19e582a: The corrected phase7-continue ticket invalidates the historical core fixture’s byte and custody-wording assertions; both failures reproduce on untouched base 92a36e732621b545e1e315abdc542469dea10fa1.

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.5

## Predicted vs actual

Stopped within the expected 60-minute budget.

