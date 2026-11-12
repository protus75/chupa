## Outcome

premise_failed

## Surprises / judgment calls

The full suite finished with 2 failures and 3456 passes. Unsettled-ticket lint also found that watch-folds-whole-journal fences chupa/__main__.py, which has a unit coverage floor of 13, without fencing a tests/unit path; it separately reported missing evidence for drain-contains-dispatch-exception. No changes were committed.

## Dead ends

The new checks require parsed Ticket fields, but the two failing tests replace validation with incomplete mock values; accommodating those mocks in production would add a defensive path unrelated to the ticket.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.10

## Predicted vs actual

Expected 45 minutes; actual not measured.

