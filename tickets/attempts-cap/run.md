## Outcome

ok

## Surprises / judgment calls

Preserved published rework on direct daemon results and documented that path’s limitation; the shakeout test now supplies an explicit premise budget.

## Dead ends

none

## Second problems filed

- box-000306-c41256c4: TicketWriter.consume_result bypasses drive’s pending-failure check and can call rework on the fifth failure; fixing it requires chupa/daemon.py outside the fence.
- box-000307-356acaee: The standalone eval/shakeout premise_park_release member needs an explicit premise_bounce budget above the new default; eval/ is outside the fence.

## Resolved engine/model

- provider: codex
- model: gpt-6.1-sol
- spec: implement 1.5

## Predicted vs actual

Completed within the expected 60-minute budget.

