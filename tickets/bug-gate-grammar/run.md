## Outcome

premise_failed

## Surprises / judgment calls

The entry unit resolves and passes its four-part depth check, but its execution semantics remain underspecified.

## Dead ends

Verified through ProcessExec that an assertion failure and a caught FileNotFoundError both return (1, '', ''); accepting arbitrary nonzero exits would admit invalid evidence.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.4

## Predicted vs actual

Stopped during contract validation, before implementation or the verification suite.

