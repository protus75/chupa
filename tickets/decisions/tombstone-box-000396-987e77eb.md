---
id: tombstone-box-000396-987e77eb
kind: tombstone
link: declined-box-000388-6e5d11b5
reopen_after_days: 30
---
A retro over one window found that requisition review parked five tickets as premise_failed (commit-lock, commit-lock-commands, requisition-stage-events, drain-detach-in-engine, qwen-provider). The findings were defects the reviewer already checks for: a floored file with no fenced unit test, a stated invariant with no named test, and unit-test criteria that touch real disk. The finding asks for author.md to get three matching preflight checks. That spec governs only the Author stage, and the finding itself says these tickets came from the human authoring path.

This is the same request that registry record declined-box-000388-6e5d11b5 already decided. That record covered a retro finding asking chupa/specs/author.md to repeat requisition review's fence rules, including the rule that a coverage-floored file needs a fenced tests/unit file. It was declined because the cited tickets were human-authored, so author.md never governed them, and because requisition review caught the defects before merge as designed. This message has the same shape. It says outright that 'the tickets in this window came from the human authoring path', so editing author.md would not have changed any of the cited runs. Its two new items (a named test for each invariant, and fakes in unit-test criteria) aim at the same repair surface for the same reason and add no Author-stage incident. Record 000376 also declined a near-identical rule that every stated invariant must map to a failing test. Reopen if a ticket written by the Author stage (source: box or another engine source) is snagged or bounced by requisition review for one of these three defects. If the real goal is to fix the human path, that is a different surface: the host authoring guide, or the chat-side review loop.

- Message text: 'The tickets in this window came from the human authoring path.' chupa/specs/author.md governs only Author-stage output.
- declined-box-000388-6e5d11b5 declined the same request (add requisition_review fence/unit-floor rules to author.md) because the cited tickets were source: human and requisition review caught the defects.
- declined-box-000376-a635ab89 declined the invariant-to-failing-test authoring rule.
- chupa/specs/author.md:18 already tells the author to fence forced files and tests that pin changed values.
- Merged tickets requisition-review-unit-floor and author-spec-ticket-rules already cover the reviewer-side floor check and binding the author to the ticket rules.

Message: box-000396-987e77eb
