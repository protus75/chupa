## Outcome

ok

## Surprises / judgment calls

Requisition-stage premise failures remain parked even if a historical terminal carries an escalation dispatch. The regression reproducer reports defect on the base commit and pass on this branch. The full suite and all host checks passed.

## Dead ends

A direct retry was rejected because it would reuse the same capability and leave the premise parked; the existing escalation ladder provides the required bounded re-offer.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.10

## Predicted vs actual

40m expected; actual time not measured.

