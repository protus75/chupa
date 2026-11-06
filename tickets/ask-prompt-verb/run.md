## Outcome

premise_failed

## Surprises / judgment calls

The existing verb-table test requires every parser verb to appear in docs/host-running.md; that file is outside the scope fence.

## Dead ends

Implemented the scoped change and ran verification; the full suite failed because the new prompt verb is absent from the host run guide.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.3

## Predicted vs actual

Expected 45 minutes; work stopped after the scope conflict was confirmed.

