---
id: declined-box-000187-b982a3cc
kind: declined
link: box-000187-b982a3cc
reopen_after_days: 90
---
A bootstrap seeding note asks section 6 of the frozen plan to write down the LLM effect key shapes for `requisition_review` calls, one for the Author path and one for the seed path. Without them, a regenerated build might let a snag re-author or a multi-seed Check replay an earlier review. The note reports no wrong replay in current code.

This only asks for plan wording. `CHUPA_PLAN.md` is frozen and never edited, so the requested change cannot be made. The note names keys the code already pins and shows no case where a review replayed wrongly. The seed path it describes was also removed by the merged `remove-seeding` ticket. Earlier records 000177 and 000185 declined similar notes that asked the frozen plan to describe effect-key overrides or name deliverables.

- Message class is suggestion, origin bootstrap-ingest, with no stage or outcome. It asks only for section 6 plan text.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Merged stems include `remove-seeding`, `requisition-author-path`, `requisition-seed-path` and `requisition-review`.
- Decision `declined-box-000177-61a7474f` declined a similar request for the plan to describe the run_seq key override used by ticketless triage calls.

Message: box-000187-b982a3cc
