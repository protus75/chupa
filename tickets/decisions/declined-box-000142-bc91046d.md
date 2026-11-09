---
id: declined-box-000142-bc91046d
kind: declined
link: box-000142-bc91046d
reopen_after_days: 90
---
The note asks for a test of a drain crash window. If the process dies after a re-offer journals `cap_consumed` but before the stem's `running` transition, the drawn retry unit stays spent. The next drain re-offers the stem with one fewer retry left. The proposed test would raise from the reentry seam and check that the draw stays counted.

This only asks for more test coverage. The note describes the current behavior (the unit stays spent after a crash) and calls for a test that pins it, not a fix. It shows no case where losing one retry unit to a crash causes incorrect runtime behavior. A crash costing one budget unit fails closed, and the cap stays bounded. Decision declined-box-000131-2f325e7a declined a similar crash-point test request for reconcile.

- The message class is `suggestion`, and its only request is to add a test that raises from the reentry seam.
- The note states the observed effect: the unit stays spent and the next drain re-offers with one fewer. That is a conservative, bounded result, not an incorrect one.
- No failure report, run artifact or incident shows a ticket parked wrongly or its caps exhausted because of this window.
- Decision declined-box-000131-2f325e7a declined a similar request to test a reconcile crash point.

Message: box-000142-bc91046d
