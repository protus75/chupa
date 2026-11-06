## Outcome

ok

## Surprises / judgment calls

A drain self-upgrade passes the accepted stop’s lifecycle identity to its child so the child can honor the journaled request.

## Dead ends

An initial checkpoint wrapper changed pause timing; it was replaced with one that preserves the existing checkpoint behavior.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.2

## Predicted vs actual

Expected 60 minutes; completed within the budget.

