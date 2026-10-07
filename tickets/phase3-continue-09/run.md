## Outcome

premise_failed

## Surprises / judgment calls

All five required entry units passed entry_unit_gap and resolve_plan_contract, but 19.P3.admission-holds-activation retains the unchanged-drain-suite requirement.

## Dead ends

Traced main → pipeline → prepare_pipeline → bind and drain → build_control; carrying one inbox through drain, bind, or Checkout requires migrating direct callers in tests/test_drain.py, which the contract declares unchanged.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.1

## Predicted vs actual

Stopped during read-first validation, before authoring or Verification, well within the 60-minute expected budget.

