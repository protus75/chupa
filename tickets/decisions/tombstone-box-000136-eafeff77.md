---
id: tombstone-box-000136-eafeff77
kind: tombstone
link: reject-queue-verbs
reopen_after_days: 30
---
A bootstrap note said that when a ticket was parked because its caps were spent, drain only reported it. It did not journal the arrival in the Reject queue (`routed: reject_queue`) that section 11.2 requires, and the note expected the Phase 2 Reject queue to fix this. That queue has now shipped. The terminal handler marks cap-spent runs as Reject-queue arrivals, and they can be released.

The gap is already closed in current code. In `chupa/runner.py`, when the attempts cap is spent (line 374) the terminal is set to `dispatch = "reject_queue"`. When `spent(...)` returns true (lines 390-391, 409), the run is routed. Every routed terminal gets `terminal["routed"] = "reject_queue"` (line 413). `status.reject_queue`, drain and the release verbs all read that field. The merged ticket reject-queue-verbs delivered the Reject queue and its release path that the note was waiting for.

- chupa/runner.py:374-377: an attempts-cap spend sets dispatch to reject_queue
- chupa/runner.py:390-391: any spent cap sends the run to reject_queue
- chupa/runner.py:412-413: terminal["routed"] = "reject_queue" is journaled on the state_transition
- chupa/status.py:35-45: reject_queue() folds routed == reject_queue arrivals
- chupa/drain.py:81,92,600-608: drain reads Reject-queue arrivals
- merged: reject-queue-verbs, plan-bound-reject-release

Message: box-000136-eafeff77
