---
id: declined-box-000151-d206f44b
kind: declined
link: box-000151-d206f44b
reopen_after_days: 90
---
A bootstrap note said that when a premise park was released, the re-offer drew a `retry` unit, even though section 11.1 charges `premise_failed` to the `premise_bounce` cap. A stem with no retries left would then stay parked even after its ticket was edited. The note asked that the re-offer draw `premise_bounce` once the Phase 2 caps existed. Current code already does this.

The problem is gone. `record_reoffer` in `chupa/drain.py` draws `retry` only when the last terminal state is not `premise_failed` and has no provider drought. A premise park is charged once, to `premise_bounce`, when it fails: `chupa/runner.py` consumes `premise_bounce` for a `premise_failed` outcome other than `render_over_bound`. So a released premise park does not spend `retry`, and a stem with no retries left is not held by a spent `retry` cap.

- chupa/drain.py:95-96: `if body.get("to") != PREMISE and "provider_drought" not in body: caps.consume(journal, stem, "retry", ...)`. The re-offer after a premise park draws no retry.
- chupa/runner.py:232-235: `premise_failed` (not over-bound) consumes the `premise_bounce` cap.
- chupa/caps.py:10: CAPS includes `premise_bounce`; chupa/config.py:175 sets `premise_bounce: Count = 1`.

Message: box-000151-d206f44b
