---
id: tombstone-box-000113-5d377ece
kind: tombstone
link: declined-box-000095-a9ffd3fe
reopen_after_days: 30
---
A bootstrap note says the production `runner.pipeline` binding behind `run <stem>` still refuses because nothing chains the stage runner into `merge.merge`. It also says nothing journals the non-ok terminal transition, since merge journals only `to: merged`. The note asks to bind the production pipeline together with a non-ok terminal handler.

Registry record declined-box-000095-a9ffd3fe covers the same gap: the production `runner.pipeline` binding refused with exit 2 until the stages and merge were chained together. That record found the chaining now exists. Later records confirm terminal transitions are journaled. Record 000083 says `run_seq` is now worked out from terminal events in the journal. Merged tickets such as run-lifecycle-steps, merge-queue and shakeout-merge show the run -> stages -> merge path working end to end. The message adds no new evidence of a current failure.

- declined-box-000095-a9ffd3fe: the production runner.pipeline binding refused with exit 2 until the stages and merge were chained together; that chaining now exists
- declined-box-000083-348a0717: run_seq is now worked out from terminal events in the journal, so terminal transitions are written
- Merged stems include run-lifecycle-steps, merge-queue, merge-queue-activation, shakeout-merge and shakeout-runner, which exercise the composed pipeline
- origin is bootstrap-ingest, a note from the bootstrap phase, not a report of a current failure

Message: box-000113-5d377ece
