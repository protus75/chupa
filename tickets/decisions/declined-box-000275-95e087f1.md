---
id: declined-box-000275-95e087f1
kind: declined
link: box-000275-95e087f1
reopen_after_days: 30
---
The note says the runner sends a ticket that ends `already_satisfied` at Check through diagnosis and into the Reject queue. In current code, `drive` handles `already_satisfied` before harvest, diagnosis and caps. It journals a settled `to: already_satisfied` transition, removes the worktree and returns. That outcome never reaches diagnosis or the Reject queue.

Nothing shows this happens in current code. `chupa/runner.py:215-219` deals with `result.outcome == "already_satisfied"` before `harvest_failure`, the cap checks, `failure_terminal` and the diagnosis call at lines 220+. `run_stages` stops before Review on this outcome (`chupa/stages.py:1527`). `already_satisfied` is in `SETTLED` (`chupa/status.py:16`), so drain treats it as settled and does not park it. The message names no stem, journal event or reproduction, and the shakeout-report-lane run artifacts only mention outbox-lift validation, not this behavior. The note looks like a stale observation from an earlier runner, and merged `already-satisfied-settles` has since reworked this path.

- chupa/runner.py:215-219: the already_satisfied branch journals the settled transition and returns before harvest_failure, failure_terminal and diagnosis
- chupa/stages.py:1527-1528: run_stages stops before Review on already_satisfied and settles it as a no-op
- chupa/status.py:16: SETTLED includes already_satisfied
- tickets/shakeout-report-lane/attempts/3/harvest.json mentions only outbox-lift artifact validation, not an already_satisfied diagnosis or Reject-queue routing
- Merged stem already-satisfied-settles covers settling this outcome

Message: box-000275-95e087f1
