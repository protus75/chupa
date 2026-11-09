---
id: tombstone-box-000130-ec9c8612
kind: tombstone
link: declined-box-000116-f4ed6b34
reopen_after_days: 90
---
If the process crashes after `write_squash` lands the squash commit on main but before the `merge/<stem>/<attempt>` effect completion and the `to: merged` transition are journaled, reconcile later reaps the orphaned intent to `abandoned`. Main still carries the merge. The note asks reconcile to check whether the squash already landed before it picks a terminal state.

Registry record declined-box-000116-f4ed6b34 covers the same crash window: a crash inside the merge effect after the commit lands on main but before its completion is journaled. It also covers the same missing recovery: nothing in `chupa/reconcile.py` maps the `chupa-ticket` trailer on main back to the ticket to settle it as merged. This note describes the same gap from reconcile's side (reaping to `abandoned`) and does not report a new incident, so it duplicates that record.

- declined-box-000116-f4ed6b34 describes the crash after commit and before the completion record in `write_squash` (`chupa/merge.py`), and says reconcile does not use the `chupa-ticket` trailer to recover.
- The message has origin bootstrap-ingest and reports no observed occurrence of this crash.

Message: box-000130-ec9c8612
