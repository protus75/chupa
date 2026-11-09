---
id: tombstone-box-000273-5e1efc68
kind: tombstone
link: declined-box-000187-b982a3cc
reopen_after_days: 90
---
A bootstrap seeding note asks section 6 of the frozen plan to state the LLM effect key shapes used for `requisition_review` calls on the Author path and the seed path, so that a regenerated build cannot let a snag re-author or a multi-seed Check replay an earlier review. It also mentions a generic async `review` hook on `LlmStage`.

Registry record declined-box-000187-b982a3cc already decided this request: write the requisition_review key shapes into plan section 6 to prevent replay between re-authors or seeds. Both notes ask only for plan wording and report no wrong replay in current code. Since then the frozen plan has stopped being edited, and the seeding lane has been removed (`remove-seeding` merged), so the seed-path key no longer exists.

- declined-box-000187-b982a3cc covers the same request: requisition_review effect key shapes for the Author path and the seed path, to be written into section 6
- CHUPA_PLAN.md is frozen and never edited (CLAUDE.md section A)
- Merged ticket remove-seeding removed the seed lane, so the seed-path key shape is obsolete
- The message reports no observed replay of an earlier review

Message: box-000273-5e1efc68
