---
id: tombstone-box-000285-e7af6bbb
kind: tombstone
link: requisition-review-bare-json-reply
reopen_after_days: 30
---
The requisition reviewer's reply on phase6-continue-02 attempt 0 began with a prose sentence before the JSON verdict. The reply failed the schema check and was recorded as an authoring_error, so the reviewer's correct spec_gap findings were lost and one gap surfaced only a full seeding attempt later. The proposed repair is to make the spec's 'ONLY one JSON object' rule stand out more and to state that any lead-in prose makes the verdict invalid.

Open ticket requisition-review-bare-json-reply already covers this failure: the requisition reviewer puts prose (and a code fence) around its verdict JSON, which breaks the 'ONLY one JSON object' contract in chupa/specs/requisition_review.md. The rejected reply then costs a retry even though the review itself was valid. This retro finding is one more instance of the same failure (phase6-continue-02 instead of phase3-continue-02/-09/-12), and it proposes a repair to the same spec file. The overcorrection concern about fenced replies belongs in that ticket's design, not in a separate ticket.

- The message describes a requisition_review reply rejected as schema-invalid because prose came before the JSON verdict, on phase6-continue-02 attempt 0.
- Open ticket requisition-review-bare-json-reply describes the same failure: the reviewer wraps its verdict JSON in a prose paragraph and fence, which breaks the 'ONLY one JSON object' contract in chupa/specs/requisition_review.md and costs an extra attempt.
- The message's proposed_spec_paths is chupa/specs/requisition_review.md, the same spec file that open ticket targets.

Message: box-000285-e7af6bbb
