---
id: declined-box-000073-375ea556
kind: declined
link: box-000073-375ea556
reopen_after_days: 90
---
A bootstrap note says the eval fixture layout has a mismatch. Each case directory holds `ticket.md`, `diff.patch` and `expected.json`, but section 7 of the frozen plan says an eval case is one closed envelope file. The note warns that a GO-grade set of 65 or more cases would add about 195 files, over the 30-file diff budget. It asks for the plan to be reconciled before `go-grade-machinery` grows the set.

This is a mismatch between the plan's wording and the fixture layout, not a runtime behavior gap. `CHUPA_PLAN.md` is a frozen design record, so the requested fix (reconcile in the plan) cannot be made. `go-grade-machinery` and `go-grade-run` have both merged, so the timing concern the note raises has passed. The file-count worry is about ticket diff size, not wrong engine behavior. Nothing shows that a ticket failed or that an eval gave a wrong result because of the per-case directory layout.

- Message class is suggestion from bootstrap-ingest; the requested fix is a plan edit.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Merged stems include go-grade-machinery and go-grade-run, so the work the note wanted to get ahead of has already merged.
- No failure report, stage, or outcome links the fixture directory layout to incorrect runtime behavior.

Message: box-000073-375ea556
