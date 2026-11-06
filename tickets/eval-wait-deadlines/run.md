## Outcome

ok

## Surprises / judgment calls

The regression test holds recovery dispatch until more than 100,000 turns have elapsed, making the old-bound failure deterministic.

## Dead ends

An initial test barrier targeted the drought dispatch and stalled; moving it to the recovery dispatch reproduced the intended failure.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.0

## Predicted vs actual

Expected 20 minutes; completed in approximately 3 minutes.

