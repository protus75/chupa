---
id: declined-box-000095-a9ffd3fe
kind: declined
link: box-000095-a9ffd3fe
reopen_after_days: 90
---
A bootstrap note described the `run <stem>` handler order: journal `to: running`, then call the stage seam, which owns the single terminal transition. It also said the production `runner.pipeline` binding refused with exit 2 until the stages and merge composition replaced its body. That composition now exists, so the note no longer describes current code.

This is a progress note, not a report of a behavior gap. In `chupa/runner.py`, `pipeline` (line 88) now returns a `PreparedDispatch` that builds the real stage composition through `prepare_pipeline` and calls it for each ticket. It no longer refuses with exit 2. Merged tickets such as run-lifecycle-steps, shakeout-stages and merge-queue-activation cover the stages and merge wiring. No harmful behavior remains to fix.

- chupa/runner.py:88 `def pipeline(checkout)` returns PreparedDispatch, which awaits `prepare_pipeline(local)` and calls the prepared callback per ticket
- In `chupa/runner.py`, the exit-2 `Refusal` is now raised only for intake failures (lines 535 and 629), not as a placeholder pipeline
- Merged stems include run-lifecycle-steps, shakeout-stages, merge-queue-activation and phase2-exit

Message: box-000095-a9ffd3fe
