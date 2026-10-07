## Outcome

premise_failed

## Surprises / judgment calls

All five required entry units passed entry_unit_gap and resolve_plan_contract; the approved phase3-continue-10 seed remains untouched.

## Dead ends

Tracing main -> pipeline -> prepare_pipeline -> bind and drain -> build_control found separate construction paths with no inbox carrier; signature or Checkout changes require callers that the contract declares preservation-only.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.1

## Predicted vs actual

Stopped during read-first contract validation, before implementation.

