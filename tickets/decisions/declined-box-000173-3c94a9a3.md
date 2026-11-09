---
id: declined-box-000173-3c94a9a3
kind: declined
link: box-000173-3c94a9a3
reopen_after_days: 90
---
A bootstrap handoff note says frozen-plan unit 19.P2 never says who runs the one-time ingest of `bootstrap/suggestions.md`. In practice the `suggestion-box` ticket ran it as its first Verification command during Check, finding the main checkout through `git rev-parse --git-common-dir`. The note asks for 19.P2 to name that invoker.

This is a request to change the wording of the plan, not a report of wrong runtime behavior. `CHUPA_PLAN.md` is a frozen design record that is never edited. The ingest itself was taken out by the merged ticket `remove-bootstrap-ingest`, so no current code depends on an invoker being named, and nothing harmful can happen without one.

- Message class is suggestion and asks only to pin the invoker in plan unit 19.P2
- Merged stems include remove-bootstrap-ingest and suggestion-box
- Project rules: CHUPA_PLAN.md is a frozen bootstrap design record and is never edited
- Earlier plan-wording bootstrap notes were declined on the same grounds (e.g. declined-box-000167-8e1c5733, declined-box-000172-227bdc2b)

Message: box-000173-3c94a9a3
