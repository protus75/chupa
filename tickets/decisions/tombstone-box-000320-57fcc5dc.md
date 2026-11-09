---
id: tombstone-box-000320-57fcc5dc
kind: tombstone
link: implement-all-premise-findings
reopen_after_days: 30
---
Retro finding: Implement replied premise_failed partway through its full-suite verification and named only the out-of-fence files it had seen so far. The next attempt then bounced on another unfenced file (chupa/drain.py) in review-before-dispatch, which used up the premise_bounce cap. merge-skip-unchanged showed the same pattern.

This is the same failure and the same evidence that merged ticket implement-all-premise-findings already fixed. That ticket was motivated by review-before-dispatch spending one attempt per unfenced file (tests/test_seed_path.py, then chupa/drain.py, and so on). It added a rule to the premise_failed bullet in chupa/specs/implement.md: work the change through every file the acceptance criteria and Verification commands force, report each forced file outside the fence as its own finding, and never stop at the first. Stopping before the suite finishes is one way of stopping at the first file, so that rule already covers it. The incidents cited here appear to come from before that rule merged. Open ticket implement-spec-sequential-final-run separately covers running Verification commands to completion.

- chupa/specs/implement.md:59-61 already says: 'work the change through every file the acceptance criteria and `## Verification` commands force, and report each forced file outside `## Scope fence` as its own finding; never stop at the first.'
- tickets/implement-all-premise-findings/ticket.md (merged) cites review-before-dispatch's five attempts on 2026-11-06, each naming one more unfenced file (tests/test_seed_path.py, chupa/drain.py, ...), which is the same run this finding cites.
- Open ticket implement-spec-sequential-final-run requires each Verification command to run whole and in sequence, with the final result reported.

Message: box-000320-57fcc5dc
