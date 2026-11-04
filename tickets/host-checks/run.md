## Outcome

premise_failed

## Surprises / judgment calls

The required host-mechanical tests passed (10 tests), and unchanged merge-queue tests passed (74 tests). The red-streak case fails independently with this implementation and passes on untouched base 2999950783460f46c56fb1247b0e00805f20d4e8. The always-failing host-red fixture is base-red at Check, so its existing merge refusal remains consistent with the explicit base-red exemption.

## Dead ends

The initial full-suite run also invalidated a source-snapshot test because formatting edits occurred after collection; that test passes independently.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.5

## Predicted vs actual

60m expected; stopped during verification after confirming the ticket restriction blocks completion.

