---
id: declined-box-000101-8a149c25
kind: declined
link: box-000101-8a149c25
reopen_after_days: 90
---
The note asked to name or pin the Outcome used when Implement or Review refuses an over-bound prompt render, so the Phase 2 premise_bounce cap would not count it. The code already keeps the two apart. The outcome stays `premise_failed` with a `render_over_bound` finding. `chupa/runner.py` does not draw `premise_bounce` for that finding and skips diagnosis. `chupa/drain.py` does not send such a park to the Reject queue and gives it its own paved road.

The cap mix-up the note warned about cannot happen. `runner.py:232-236` works out `over_bound` from the `render_over_bound` finding code and calls `consume(..., "premise_bounce", ...)` only when `over_bound` is false. Drain's settle and premise-road logic (`drain.py:604`, `drain.py:654`) also check for that reason code. Adding a new Outcome member would change only the vocabulary, not what the code does at runtime.

- chupa/runner.py:232-235: `over_bound = result.outcome == "premise_failed" and any(f.code == "render_over_bound" ...)`; premise_bounce is consumed only `if result.outcome == "premise_failed" and not over_bound`
- chupa/runner.py:236: `diagnosed = result.outcome != "budget_exceeded" and not over_bound`, so an over-bound render gets no diagnosis call
- chupa/drain.py:604-605: an over-bound premise park skips `reject_arrival` routing
- chupa/drain.py:654-655: an over-bound park gets the paved road 'shrink or split the committed ticket text and rerun drain'
- Registry tombstone-box-000051-5b0486d6 / merged spine-diagnosis already covers how RenderOverBound becomes `premise_failed`

Message: box-000101-8a149c25
