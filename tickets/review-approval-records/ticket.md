---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- chupa/rework.py
- chupa/author.py
- tests/test_rework.py

## Goal / Why
`review-before-dispatch` will run a requisition review before a ticket's first run unless the journal holds a `requisition_verdict` `approve` for its exact committed content. The Author stage (`chupa/author.py`) and `chupa review` journal that record, but Rework reviews every split or update proposal it publishes and journals nothing, so each Rework successor would be reviewed a second time at dispatch. After this change an approved Rework proposal carries the same approve record. Rework already commits exactly the reviewed bytes (`record_supersedes` refuses a committed successor that differs from its reviewed proposal), so the record's `ticket_sha` is the committed blob.

## Scope in / Scope out
- In: `chupa/rework.py`: where Rework's review closure gets an `approve` verdict from `review_ticket` for a proposal, journal SIGNAL `requisition_verdict` with exactly the body keys `chupa/author.py` writes (`verdict`, `ticket_sha`, `provider`, `model`, `spec_version`), with `ticket=` the proposal's stem. Journal nothing for `snag` or `rma`.
- In: `tests/test_rework.py`: add `test_approved_proposals_journal_requisition_approval`: a split with two approved proposals journals exactly two `requisition_verdict` approve records, one per proposal stem, each `ticket_sha` equal to the git blob sha of that proposal's text (fails if a proposal has no record, or if a snagged proposal gets one).
- Out: `chupa/requisition.py`, the review prompt, `chupa/author.py`, dispatch, `drive`.

## Scope fence
- chupa/rework.py
- tests/test_rework.py

## Acceptance criteria
1. Each approved Rework proposal gets one `requisition_verdict` approve keyed to its blob and a snagged one gets none, checked by `uv run pytest tests/test_rework.py -k approved_proposals_journal_requisition_approval`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_rework.py -k approved_proposals_journal_requisition_approval
uv run pytest -q
```

## Definition of rejected
A record is journaled for a non-approve verdict; the body keys differ from the Author stage's; any behavior other than the added journal record changes.

## Time budget
- expected: 20m
- stuck: 60m
