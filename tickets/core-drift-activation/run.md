## Outcome

premise_failed

## Surprises / judgment calls

The untouched branch equals its merge base and contains dormant classifier code, not the previous attempt’s activation diff.

## Dead ends

Verified on the untouched base that Git._run replaces a committed non-UTF-8 byte with U+FFFD; encoding its output cannot recover the original bytes.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.4

## Predicted vs actual

none

