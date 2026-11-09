---
id: declined-box-000071-0db3090f
kind: declined
link: box-000071-0db3090f
reopen_after_days: 60
---
A bootstrap note says Claude's read-only surfaces (review, author) run with their working directory set to the main checkout, not the ticket worktree. Review sees the change only as the diff in its rendered prompt. The note asks the plan's section 6 to say which tree a read-only reviewer may browse, and suggests the ticket worktree.

This asks for a change to plan wording, and `CHUPA_PLAN.md` is frozen. The note reports no review that went wrong because the reviewer browsed main instead of the worktree, such as a wrong approval or a false finding on pre-change files. Without such an incident there is no current harmful behavior and no measurable repair to build. The open ticket claude-readonly-hard-tool-restriction covers what these surfaces may do, not which tree they run in, so this is not a duplicate.

- The message class is suggestion, its origin is bootstrap-ingest, and it reports no stage or outcome.
- The requested change is to plan section 6 text. CLAUDE.md says CHUPA_PLAN.md is frozen and never edited.
- The note gives no example of a review verdict made wrong by reading files in the main checkout.
- claude-readonly-hard-tool-restriction covers tool permissions on read-only surfaces, not their working directory.

Message: box-000071-0db3090f
