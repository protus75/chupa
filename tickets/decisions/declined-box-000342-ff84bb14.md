---
id: declined-box-000342-ff84bb14
kind: declined
link: box-000342-ff84bb14
reopen_after_days: 30
---
The note proposes an authoring rule for tickets that copy a block from another document verbatim and say the block wins on any difference. Such a ticket would have to be written or re-reviewed after the source block's last change merges, and would have to name the keys it copies. The motivating case is chupa-test-gates, which parked on a contradiction after the python-host block in docs/host-contract.md grew after the ticket was written.

There is one incident, and it is closed. chupa-test-gates is now in the merged set, so nothing is blocked today. Its Scope in already names the keys it copies (the `review.autofix` and `review.mechanical` entries of the `python-host` block), so the 'name the keys' half was already true when it parked. What is left is a rule about when a ticket should be authored, based on one ticket whose park was cleared with a ticket edit. The message shows no reachable runtime misbehavior that recurs, and no open ticket that is stuck on the same pattern. It also gives no measurable post-change observation that a single spec or gate change could deliver. Existing requisition-review closure tickets (requisition-review-data-file-consumers, set-membership-fence-closure) already handle the nearby problem of a ticket contradicting a file it does not fence.

- tickets/chupa-test-gates/ticket.md:35 Scope in copies the `review.autofix` and `review.mechanical` entries of the `python-host` block in `docs/host-contract.md` verbatim, 'on any difference in those entries, the block wins', so it already names the copied keys
- chupa-test-gates appears in the merged stems list, so the park was released and the ticket landed
- The message cites no second ticket that parked on a verbatim-copy contradiction with a block that grew after it was written

Message: box-000342-ff84bb14
