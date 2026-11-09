---
id: tombstone-box-000272-83206fa0
kind: tombstone
link: declined-box-000186-2077a583
reopen_after_days: 90
---
A bootstrap seeding note says no Phase 2 deliverable built the minimal `auth_error` provider classification required by the 19.P2 battery member and the provider-failures contract. Prompt 17 placed it in `shakeout-providers`, which fenced two modules (`chupa/providers.py` and `chupa/driver.py`) even though 19.P2 says a fixture ticket fences one. The note asks 19.P2 to name the owning module.

This repeats the request in registry record declined-box-000186-2077a583: the same missing `auth_error` classification, the same two-module fence in `shakeout-providers`, and the same ask to name the owner in 19.P2. That record already declined it. The ask is a wording change to the frozen plan, with no reachable incorrect runtime behavior. `shakeout-providers` and `provider-cooldown-failover` have both merged.

- Registry record declined-box-000186-2077a583 describes the same `auth_error` ownership gap and the same request to pin the owner in 19.P2.
- `shakeout-providers` and `provider-cooldown-failover` are both in the merged stems list.
- CHUPA_PLAN.md is a frozen design record and is never edited, so a plan-text change to 19.P2 cannot be a buildable ticket.

Message: box-000272-83206fa0
