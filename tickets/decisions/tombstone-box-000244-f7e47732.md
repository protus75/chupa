---
id: tombstone-box-000244-f7e47732
kind: tombstone
link: declined-box-000117-cdc4c20b
reopen_after_days: 90
---
If the process crashes after `write_squash` stages `merge --squash` on main but before `commit` runs, main's index stays dirty. The note asks reconcile or a tree-hash check to find that staged squash and reset it, so the replayed `merge --squash` is not refused.

This is the same crash window and the same request as registry record declined-box-000117-cdc4c20b: a staged squash left on main's index after a crash between `merge --squash` and `commit`, and a proposal that reconcile or a tree-hash assert detect and reset it. That record already found that on replay `dirty_overlap` refuses with a `dirty_checkout` finding that carries a paved road. The message gives no new evidence.

- registry declined-box-000117-cdc4c20b: same crash point in `write_squash` (`chupa/merge.py`), same reconcile/tree-hash reset proposal
- message origin is bootstrap-ingest with no new stage, outcome or incident

Message: box-000244-f7e47732
