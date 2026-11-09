---
id: declined-box-000374-ab00980b
kind: declined
link: box-000374-ab00980b
reopen_after_days: 14
---
A session report bundles three separate Author-stage defects seen while authoring claude-effort-flag. (1) An Author retry (call 4) fixed a gate_bypass finding but dropped the fence and Context entries that call 3 had added correctly, even though the spec says to keep already-valid sections byte-identical. (2) The ticket_schema fix hint for gate_bypass does not say the field is a list, so the model wrote `gate_bypass: false`. (3) The Author prompt never gets the coverage_dependents data that requisition review gets, so Author cannot find test files that run the changed sources.

The report has three unrelated repairs: Author retry regression, ticket_schema hint wording, and coverage_dependents input to Author. Each needs its own ticket, fence and measurable outcome, so the message is not bounded to one buildable ticket. The code backs claim (3): `chupa/requisition.py:118-138` computes `coverage_dependents` only for the requisition_review render, and `chupa/specs/author.md` has no such input. Requisition review already snags any unfenced dependent, so the missing input costs extra Author rounds but does not let bad work through. Claims (1) and (2) rest on one run (claude-effort-flag calls 3-4), with no repeat rate and no cost figure, and the message names no post-change observation for any of the three. No open or merged ticket duplicates them: requisition-coverage-dependents covers only the review side, and set-membership-fence-closure covers a different closure.

- chupa/requisition.py:118-138 builds coverage_dependents only for the requisition_review render
- chupa/specs/requisition_review.md:60-62 takes a coverage_dependents data block; chupa/specs/author.md has none
- chupa/tickets.py:61 types gate_bypass as list[GateBypass]; the message says the fix hint does not name the list shape
- The report cites one Author run (claude-effort-flag, calls 3 and 4) and gives no repeat rate or cost
- Merged requisition-coverage-dependents gives dependents to review only, not to Author

Message: box-000374-ab00980b
