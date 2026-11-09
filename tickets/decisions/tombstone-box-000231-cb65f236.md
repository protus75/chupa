---
id: tombstone-box-000231-cb65f236
kind: tombstone
link: declined-box-000080-9f4318de
reopen_after_days: 60
---
The review eval harness scores its fixtures one at a time in a single process, which takes about 8 minutes for 22 fixtures. A builder limited to 10 minutes per command had to run it detached and poll. The note suggests saving each fixture's score as it finishes so a run can resume, before the GO-grade set grows past 50 fixtures.

Registry record declined-box-000080-9f4318de already decided this request: serial single-process eval scoring, the 10-minute headless command limit worked around by a detached run, and per-fixture resumable scoring before the set grows past 50. This message says the same thing, so it duplicates that record.

- The message describes 22 serial opus calls (~8 min), a 10-minute per-command limit worked around by a detached launch plus polling, and proposes per-fixture journaled or spooled scoring before 50+ fixtures.
- declined-box-000080-9f4318de: the review eval harness scores 22 fixtures one after another in one process (~8 min); a headless builder with a 10-minute limit ran it detached and polled; it proposes saving each fixture's score so a run can resume before the GO-grade set grows past 50.
- eval-wait-deadlines is merged, and no open ticket targets per-fixture resumable eval scoring.

Message: box-000231-cb65f236
