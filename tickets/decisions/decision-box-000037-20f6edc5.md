---
id: decision-box-000037-20f6edc5
kind: decision
link: box-000037-20f6edc5
reopen_after_days: 60
---
The frozen plan defines a separate, soft-by-default severity for gates that run at authoring time. `chupa/gates.py` has only the merge-context severity map (`merge_severity`). The suggestion is to add an author-context severity constant and wire its first author-time gate consumer, such as requisition review or the ticket schema check.

No gate runs at authoring time through `run_gates`. Its only callers are the check stage, the merge queue, merge, and the driver's stage gates, and all of them use merge-context or explicit severities. So no gate is currently mis-severitied at authoring time, and no reachable runtime behavior is wrong. Requisition review and ticket-schema validation already enforce authoring quality on their own paths. Adding the constant now would be plan-alignment work with no consumer, which is speculative accretion. No open ticket or merged stem covers it, so this is not a duplicate.

- chupa/gates.py:90 merge_severity is the only severity map builder; no author-context constant exists
- run_gates callers: chupa/stages.py:1381, chupa/mergequeue.py:318-333, chupa/merge.py:166/295/297, chupa/driver.py:366, none of which is an author-time gate
- Merged requisition-review and author-stage tickets enforce authoring checks without run_gates

Message: box-000037-20f6edc5
