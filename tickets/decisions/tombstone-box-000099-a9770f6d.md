---
id: tombstone-box-000099-a9770f6d
kind: tombstone
link: reject-queue-verbs
reopen_after_days: 30
---
The note asked whether `run <stem>` should refuse a rejected stem once the Reject queue existed, because re-running would bypass its `confirm` release. The Reject queue has landed, and `run` now refuses a rejected stem. `reject_ticket` in `chupa/runner.py` sets `state: rejected` in `ticket.md`, commits it, and journals `to: rejected`. The `run` path refuses any ticket whose state is not `confirmed`, and drain and the scheduler skip stems whose state is `rejected`.

The decision the note put off was made when the Reject queue verbs merged. Current code refuses to re-run a rejected stem in every dispatch path, so no harmful gap is left. This duplicates the merged reject-queue-verbs work.

- chupa/runner.py:582-588 reject_ticket sets state: rejected in ticket.md, commits it, and journals to: rejected
- chupa/runner.py:641-642 run refuses a ticket whose state is not confirmed and gives the operator a next step
- chupa/drain.py:50-51 RETIRED = {rejected}: never dispatched again; chupa/drain.py:420 skips SETTLED | {rejected}
- chupa/scheduler.py:69 leaves out stems in SETTLED | {rejected}
- chupa/__main__.py:531,815 review and order refuse stems that are settled or rejected

Message: box-000099-a9770f6d
