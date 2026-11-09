---
id: tombstone-box-000233-d5b3f5db
kind: tombstone
link: declined-box-000083-348a0717
reopen_after_days: 90
---
A bootstrap note says no code writes terminal `state_transition` events, so `run_seq` stays 0 for every stem. A second run of the same ticket and attempt in a shared state directory would then replay the first run's recorded LLM calls. The note expected the `run <stem>` verb's terminal journaling and reconcile-on-entry to close the gap.

Registry record declined-box-000083-348a0717 covers the same note: same `run_seq`=0 replay gap, same expected fix. That record found both pieces have shipped. The `run` path and drain journal terminal transitions, reconcile reaps orphans, and `run_seq` is derived from the journal's terminal events. This message duplicates that record.

- declined-box-000083-348a0717 describes the same `run_seq`=0 replay gap and its expected closure by `run <stem>` terminal journaling plus reconcile-on-entry, and records that both exist now
- Merged stems include spine-harvest and reject-queue-verbs, which journal terminal transitions; registry record 000150 cites `chupa/runner.py` journaling `to: running` with `ticket_sha`, and records 000098/000124 note reconcile-on-entry reaps orphaned runs

Message: box-000233-d5b3f5db
