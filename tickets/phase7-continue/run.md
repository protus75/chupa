## Outcome

premise_failed

## Surprises / judgment calls

Config accepts host_lint, but GateBypass rejects that code because it accepts only engine codes; both production files were verified identical to base dac13fa7a3306da0e978bd62c302fd520fda9a1c.

## Dead ends

Removed the draft seeds and snapshot after discovering the contract gap. Snapshot and plan-lint tests passed; the full suite was interrupted after 1219 passing tests.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.5

## Predicted vs actual

Stopped within the 60-minute expected budget.

