---
id: declined-box-000184-cf6a75ef
kind: declined
link: box-000184-cf6a75ef
reopen_after_days: 90
---
A bootstrap handoff review note said the `box-start-policy` ticket listed `escalation-ladder` as a dependency with no code reason, only to make the batch run in order. It asked to drop the edge or say in the ticket that it exists for ordering.

Both tickets have merged, so the edge cannot block or reorder anything now. The note describes ticket metadata and shows no wrong runtime behavior. The current rule that `depends` names only a ticket whose merged code this one needs is already in CLAUDE.md, so no ticket is needed.

- `box-start-policy` and `escalation-ladder` are both in the merged list.
- CLAUDE.md engine conduct: 'Use depends only for a ticket whose merged code this one needs; put all other ordering in priority or Runs before.'
- This is a ticket-authoring note about two merged tickets and reports no runtime failure.

Message: box-000184-cf6a75ef
