---
id: tombstone-box-000251-2673f0c1
kind: tombstone
link: already-satisfied-settles
reopen_after_days: 30
---
This message says two journal forms record a ticket that was already satisfied. `runner.drive` writes `to: already_satisfied`, but section 7 says the no-op settles as `to: merged`, and drain's SETTLED set accepts both. It asks to keep one form and remove the other from `drain.SETTLED`. The merged ticket `already-satisfied-settles` already handled this.

Registry record tombstone-box-000134-f076a55f raised the same issue: the `already_satisfied` and `merged` journal forms, with drain SETTLED accepting both. That record was tombstoned to the merged ticket `already-satisfied-settles`. This message is a semantic duplicate, so it links to the same ticket.

- Registry tombstone-box-000134-f076a55f covers the same two-form issue and links to already-satisfied-settles
- already-satisfied-settles appears in the merged stems list

Message: box-000251-2673f0c1
