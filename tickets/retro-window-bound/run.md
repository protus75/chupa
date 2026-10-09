## Outcome

premise_failed

## Surprises / judgment calls

The targeted verification yielded 157 passes and one failure: the drain selected-failure scenario expected one retro attempt, but the required behavior produced two; that test passes on the unchanged base.

## Dead ends

Implemented and tested the scoped fixes, then restored them because updating the contradictory drain assertions is forbidden by the fence.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.2

## Predicted vs actual

45m expected; approximately 10m spent.

