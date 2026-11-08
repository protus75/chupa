## Outcome

premise_failed

## Surprises / judgment calls

The in-scope implementation passed all 3,161 tests, but Git output is decoded with replacement, so it cannot supply the original bytes for non-UTF-8 conduct files. I rejected re-encoding that text because it loses committed bytes.

## Dead ends

Using the existing text-returning Git seam passes the suite but does not meet the byte-exact contract.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.3

## Predicted vs actual

Expected 30 minutes; the full test suite completed in about one minute.

