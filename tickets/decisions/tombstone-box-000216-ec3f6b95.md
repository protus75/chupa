---
id: tombstone-box-000216-ec3f6b95
kind: tombstone
link: tombstone-box-000051-5b0486d6
reopen_after_days: 90
---
A bootstrap note says nothing turns a `RenderOverBound` raised during prompt rendering into a stage outcome, so it would escape `Driver.run`. It asks for a mechanical pre-call check that parks the ticket as `premise_failed` without a diagnosis call, plus a test that no LLM call is made.

Registry record tombstone-box-000051-5b0486d6 covers the same gap and found the handling already built by merged ticket spine-diagnosis. Record declined-box-000101-8a149c25 also confirms what current code does: an over-bound render ends `premise_failed` with a `render_over_bound` finding. `chupa/runner.py` skips diagnosis and does not draw `premise_bounce` for that finding, and `chupa/drain.py` gives such a park its own paved road.

- tombstone-box-000051-5b0486d6: same RenderOverBound to premise_failed short-circuit request, found already handled (link spine-diagnosis)
- declined-box-000101-8a149c25: an over-bound render outcome is premise_failed with a render_over_bound finding, and diagnosis is skipped in chupa/runner.py
- spine-diagnosis is in the merged stems

Message: box-000216-ec3f6b95
