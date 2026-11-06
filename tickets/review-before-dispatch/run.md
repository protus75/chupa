## Outcome

premise_failed

## Surprises / judgment calls

Drain automatically re-offers a Reject-queued ticket with remaining cap budget; requisition snags consume no cap, so they require an explicit operator hold.

## Dead ends

Considered reusing the ticket_changed hold marker, but that would falsely report a ticket change instead of the review findings.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.1

## Predicted vs actual

The ticket budget was 75 minutes expected and 90 minutes stuck; work stopped after identifying the scope conflict.

