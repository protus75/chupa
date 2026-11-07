---
id: tombstone-box-000051-5b0486d6
kind: tombstone
link: spine-diagnosis
reopen_after_days: 90
---
This bootstrap note says nothing turns an over-bound prompt render (`RenderOverBound`) into a stage outcome, so the exception would escape `Driver.run`. It asks for a pre-call short-circuit that parks the ticket as `premise_failed` without a diagnosis call. That handling already exists.

Merged work has already closed the gap. `chupa/stages.py:650` catches `RenderOverBound` around `driver.run` for Implement and returns `premise_failed` with the `render_over_bound` finding and zero cost. `chupa/stages.py:1486`, `chupa/requisition.py`, `chupa/rework.py` and `chupa/retro.py` catch it the same way. `chupa/runner.py:209-213` skips diagnosis for an over-bound render and sends it to Rework. Tests cover these paths, including that no LLM call is made. Merged tickets spine-diagnosis and rework-activation specified this behavior.

- chupa/stages.py:650-652 catches RenderOverBound around driver.run and returns a premise_failed StageResult with zero cost
- chupa/runner.py:209-213 skips diagnosis when a premise_failed result carries a render_over_bound finding
- tests/test_diagnose.py:191 test_render_over_bound_calls_rework_but_not_diagnosis
- tests/test_rework.py:483 asserts requests == [] and cost.attempts == 0 for an over-bound render
- tickets/spine-diagnosis/ticket.md:58 specifies that an over-bound render gets no diagnosis, no draw and no record

Message: box-000051-5b0486d6
