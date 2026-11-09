---
id: declined-box-000375-2569b19d
kind: declined
link: box-000375-2569b19d
reopen_after_days: 30
---
Proposes that Check run only the test files the coverage map lists as dependents of a ticket's diff, so each attempt gets quicker feedback, with the full always/hard suite kept for merge integration. It also says nothing checks whether the coverage map is stale, although the map records the commit SHA it was built from.

This is a speed optimization. It does not report any wrong runtime behavior. The message names no run where Check took so long that it caused harm, such as a timeout, a breached drain ceiling or a cap spent on wall-clock time. It also names no incident where a stale coverage map gave wrong results, such as requisition review missing a coverage dependent and a ticket bouncing on an unfenced test. A dependents-only Check would also weaken the per-attempt gate: failures outside the dependent set would first show up at merge, after Review had already been paid for. The staleness point is speculative hardening until a stale map is shown to have caused a wrong fence or a missed dependent.

- The message is class `suggestion` from a session, with no stage, outcome or report attached.
- No run, attempt or retro measurement is cited that shows Check time causing a failure or a timeout.
- No incident is cited where a stale coverage map led requisition review to miss a dependent; the merged `requisition-coverage-dependents` work already uses the map.
- Open tickets `check-test-timing`, `retro-test-measurements` and `retro-test-proposals` will start recording suite and test timing. That data could later show whether Check time is actually a problem.

Message: box-000375-2569b19d
