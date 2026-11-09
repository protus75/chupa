---
id: tombstone-box-000389-d367a67b
kind: tombstone
link: requisition-review-invalid-prior-full-rereview
reopen_after_days: 30
---
Rework passes earlier failure findings to requisition review as its prior review. If those findings include an 'invalid requisition review reply' snag, the reviewer may treat a review whose reply failed the schema check as a real prior review. It would then raise new findings only against changed text and miss real defects. The note suggests rework pass no prior in that case. It reports no incident on the rework path; the only observed case came through seeding, which has since been removed.

This is the same behavior gap as open ticket requisition-review-invalid-prior-full-rereview. That ticket fixes the rule in chupa/specs/requisition_review.md that limits new findings to changed text, so a prior review whose reply failed the schema check does not count. That fix covers every caller that passes a prior review, rework included. The note proposes a rework-only change (pass prior='none'), but that is a second way to block the same failure, and the note itself says no rework incident has happened. Reopen if, after requisition-review-invalid-prior-full-rereview merges, a rework-path review still treats a schema-invalid prior review as complete and approves without a full re-review.

- The message says rework.py is the only caller left that passes a prior review, and that it has no observed incident.
- The original incident (core-drift-activation) came through seeding, which commit fcefd4f5 removed.
- Open ticket requisition-review-invalid-prior-full-rereview targets the 'NEW finding only against changed text' rule, which has no exception for a prior reply that failed the schema check, using the same core-drift-activation incident.

Message: box-000389-d367a67b
