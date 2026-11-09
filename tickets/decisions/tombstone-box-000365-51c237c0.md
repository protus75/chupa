---
id: tombstone-box-000365-51c237c0
kind: tombstone
link: requisition-review-unit-floor
reopen_after_days: 30
---
Requisition review approved three tickets that added production code to modules with a per-file unit coverage floor in test-gate.toml. None of the three fenced a tests/unit file. All three then failed the unit coverage gate, which used up their retries and premise bounces until they parked. The finding asks the review spec to check whether a fence lets new code reach its unit floor.

Merged ticket requisition-review-unit-floor was written from this same retro finding (box 000365) and covers the same three tickets and the same coverage numbers. It added the requested rule to chupa/specs/requisition_review.md. When Scope in adds statements or branches to a file whose floor in test-gate.toml is above 0, the fence must hold a tests/unit file whose tests run the new lines. If it does not, review returns a snag that names the file and its floor. That rule matches the narrowing the finding asks for to avoid overcorrection.

- tickets/requisition-review-unit-floor/ticket.md Goal cites the same three tickets and the same floors (testreport.py 10.96% vs 13%, hostfiles.py 16.39% vs 17%, reconcile.py 11.76% vs 12%)
- chupa/specs/requisition_review.md:27 now says the fence must hold a `tests/unit` file whose named tests run the new lines when Scope in adds statements or branches to a file with a floor above 0
- requisition-review-unit-floor is in the merged stems list (last change 4630a0fc, 2026-11-08)

Message: box-000365-51c237c0
