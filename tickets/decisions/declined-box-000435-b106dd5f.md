---
id: declined-box-000435-b106dd5f
kind: declined
link: box-000435-b106dd5f
reopen_after_days: 30
---
A suggestion carried over from the fungo host on 2026-11-13 asks the Acceptance criteria bullet of the host authoring guide (chupa/docs/host-authoring.md) to add three rules for writing criteria. First, a criterion may assert that something is absent. Second, a criterion should name the exact stored form of a value, such as blank becoming null or leading zeros being kept, instead of saying 'preserved' or 'as received'. Third, a placeholder for something nothing reads should use a made-up name, not a real path that a later ticket might start reading.

This only proposes wording for the authoring guide. The message says itself that no incident is cited. It names no run, ticket, review finding or retro measurement in which a vague criterion, a missing absence assertion or a real-path placeholder led to wrong runtime behavior, a failed run or a spent cap, so there is no measurable post-change observation to build against. Registry records 000431, 000432 and 000433 declined other fungo host-authoring.md rule carryovers from the same date on the same grounds. Reopen if a chupa or host run is shown failing Check, Review or a later merge because a criterion said 'preserved' or 'as received' without the exact stored form, left out a needed absence assertion, or used a placeholder path that a later ticket began reading.

- The message states 'No incident cited.'
- origin is session, and stage, outcome, report and proposed_paths are all empty
- declined-box-000431-caf1a286, declined-box-000432-6db34da4 and declined-box-000433-cc573d5a declined other fungo-sourced host-authoring.md rule proposals from 2026-11-13 because they cited no incident
- No open ticket or registry record covers these three criterion-writing rules, so a tombstone does not apply

Message: box-000435-b106dd5f
