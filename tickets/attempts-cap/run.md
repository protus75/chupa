## Outcome

premise_failed

## Surprises / judgment calls

Untouched merge base d540f701 passed both Verification commands: 104 focused tests and 3863 full-suite tests. Applying premise_bounce=1 only in memory reproduced the shakeout failure, so it is not base-red.

## Dead ends

No test-only override was added because it would leave the standalone shakeout battery broken.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6-astra
- spec: implement 1.5

## Predicted vs actual

60m expected; approximately 9m spent validating the scope blocker.

