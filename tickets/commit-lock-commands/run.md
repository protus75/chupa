## Outcome

premise_failed

## Surprises / judgment calls

The targeted verification passed 85 tests. The full unit gate failed three tests and the full integration suite failed one test because they retain old lock assumptions; lint and format passed. Changes are uncommitted.

## Dead ends

The simpler approach of leaving existing tests unchanged cannot pass the host checks because two tests explicitly require Review to acquire the engine lock and reap.

## Second problems filed

- box-000422-6260dc47: README.md:73 says Review requires the writer lock, which would be stale after this change.

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.10

## Predicted vs actual

none

