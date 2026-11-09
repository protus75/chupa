---
id: declined-box-000145-5f46e041
kind: declined
link: box-000145-5f46e041
reopen_after_days: 90
---
`chupa/stages.py` uses the private `_HEADING` pattern from `chupa/tickets.py` to find a ticket's acceptance-criteria section during re-entry rendering. The note proposes adding a public section-splitting helper to `tickets` so that `stages.py` no longer reaches into a private name.

This is an encapsulation and refactor preference. The note reports no wrong runtime behavior: re-entry still finds the criteria section correctly because both modules share one heading pattern, which is the opposite of a drift bug. Decision declined-box-000139-65491dbc already declined the same kind of request for the private `_porcelain` import. The cleanup can be done whenever `tickets.py` section parsing is next touched for a real behavior change.

- The message is classed as a `suggestion` from a bootstrap-ingest reentry-review note and names only a private-import style concern.
- It reports no failure, wrong output, or crash caused by `stages.py` importing `tickets._HEADING`.
- Precedent: declined-box-000139-65491dbc declined making the privately imported `_porcelain` helper public, for the same reason.

Message: box-000145-5f46e041
