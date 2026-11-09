---
id: declined-box-000080-9f4318de
kind: declined
link: box-000080-9f4318de
reopen_after_days: 30
---
The review eval harness scores its 22 fixtures one after another in a single process, which takes about 8 minutes. A headless builder with a 10-minute per-command limit ran it detached and polled until it finished. The note proposes saving each fixture's score as it completes so that a run can resume, before the GO-grade set grows past 50 fixtures.

This is hardening for a future fixture count. The current run finished and produced its signal; the builder only had to run it detached. No run has been lost, no score corrupted, and no gate has failed because the harness cannot resume. The harm depends on a larger fixture set and on an outside caller's time limit, not on how the engine behaves today. That falls under speculative hardening, which is declined.

- The message reports one run of about 8 minutes that completed when launched detached; it reports no failure or lost result.
- The 50+ fixture growth is described as future work in Phase 6, not as the current set.
- The 10-minute per-command limit belongs to the outside builder's environment, not to chupa's runtime.
- Merged tickets diagnosis-eval-run, go-grade-run and eval-wait-deadlines already run the eval harness as it is.

Message: box-000080-9f4318de
