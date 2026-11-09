---
id: tombstone-box-000382-f1506f53
kind: tombstone
link: requisition-review-unit-floor
reopen_after_days: 30
---
The context-sections ticket added logic to chupa/tickets.py, whose unit-only coverage floor (11%) had almost no margin, but its fence held only tests/integration files. Attempts 0 and 2 measured 10.6-10.8%, missed the floor, and premise-failed. The note asks requisition review and the author spec to flag a ticket that adds code to a floored chupa/ module without fencing a tests/unit file, with this paved road: fence a unit test and keep the new logic pure so it can be unit-tested.

The merged ticket requisition-review-unit-floor already adds this check to the requisition review spec: does the fence let new code in a module with a test-gate.toml unit floor reach that floor? Registry record tombstone-box-000365-51c237c0 already linked an equivalent finding to it. That finding covered three tickets that added code to floored modules without fencing tests/unit and failed the unit gate. The context-sections incident is one more case of the same gap. The only new part is the request for an author-spec mirror, which on its own is speculative hardening and not a separate runtime gap.

- Merged stem requisition-review-unit-floor
- tombstone-box-000365-51c237c0: requisition review approved tickets adding production code to modules with a per-file unit floor without fencing tests/unit; asked the review spec to check whether the fence lets new code reach the floor; linked to requisition-review-unit-floor
- context-sections is in the merged set, so the incident is historical
- Open ticket implement-spec-run-coverage-gate covers Implement running the hard coverage gate before replying ok

Message: box-000382-f1506f53
