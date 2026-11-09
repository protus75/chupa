---
id: declined-box-000343-d42686b0
kind: declined
link: box-000343-d42686b0
reopen_after_days: 30
---
The note warned that ticket serve-reoffer-rule had the same `## Regression` defect as shared-hold-rule. Its command, `./dev.py test tests/test_scheduler.py -k ...`, prints pytest text, but the bug_evidence gate expects exactly one `regression_result` JSON object on stdout. The note expected the ticket to fail Check because of this, and asked for Regression to be rewritten as a carried `tests/regress_*.py` reproducer before the ticket ran.

The defect the note predicted never became a current failure. serve-reoffer-rule is now in the merged set, so it either cleared bug_evidence or was fixed before it merged. No confirmed, unrun ticket is left to repair. The underlying cause is a requisition review that approves a Regression command whose output is not regression_result JSON. Open ticket requisition-review-regression-protocol-snag already covers that cause, so this note adds no new buildable work.

- serve-reoffer-rule appears in the merged stems list
- shared-hold-rule appears in the merged stems list
- open ticket requisition-review-regression-protocol-snag covers the cause: requisition review approving a non-JSON `## Regression` command

Message: box-000343-d42686b0
