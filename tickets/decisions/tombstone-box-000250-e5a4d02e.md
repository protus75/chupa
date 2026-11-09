---
id: tombstone-box-000250-e5a4d02e
kind: tombstone
link: declined-box-000116-f4ed6b34
reopen_after_days: 30
---
This is the same merge crash window that record 000116 already covers. If the process dies after `write_squash` commits the squash to main but before the merge effect's completion and the `to: merged` transition reach the journal, reconcile later reaps the orphaned merge intent as `abandoned` even though main holds the merge. The note asks reconcile to check whether the squash landed, using the `chupa-ticket` trailer or harvest, before it picks the terminal state.

Registry record declined-box-000116-f4ed6b34 already decided this crash point between the squash commit and the journal write in `chupa/merge.py` `write_squash`, including the missing trailer-based recovery in `chupa/reconcile.py`. Record tombstone-box-000130-ec9c8612 already tombstoned a note that described the same orphaned-intent-reaped-to-`abandoned` result. This note adds no new failure evidence: no recorded incident where an abandoned stem's merge actually landed on main.

- declined-box-000116-f4ed6b34 covers the window after the squash commit and before the merge completion is journaled, and the absence of `chupa-ticket` trailer recovery in reconcile
- tombstone-box-000130-ec9c8612 duplicates 000116 and describes the same symptom: the orphaned intent is reaped to `abandoned` while main carries the merge
- No open ticket covers reconcile checking whether a merge landed, and the message gives no observed incident

Message: box-000250-e5a4d02e
