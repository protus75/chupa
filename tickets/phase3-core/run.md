## Outcome

premise_failed

## Surprises / judgment calls

The shipped entry_unit_gap checker confirms all three omissions on base commit 6a061e41efc80bd1fef43c49d90e0f45f927ff50; HEAD equals that base, the working plan matches it, and git status is clean.

## Dead ends

Verification was not run because the ticket explicitly requires stopping when entry units are missing.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.1

## Predicted vs actual

Stopped during initial validation, below the 60m expected and 120m stuck budgets.

