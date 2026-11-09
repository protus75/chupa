---
id: declined-box-000385-d25d79d3
kind: declined
link: box-000385-d25d79d3
reopen_after_days: 30
---
`chupa triage` holds the checkout writer lock while its model call runs. The note proposes holding the lock only around the git and box writes, but only after journal appends get their own lock, and that lock does not exist yet.

The message describes a pattern, not an observed failure. It cites no run where a triage holding the lock blocked a confirm, reject, pause, review or drain and caused harm. The fix depends on a separate journal-append lock that has not been built, so as written it is not one buildable ticket. The closely related general rule (record declined-box-000381-d5f2e361) was already declined. The review case it was based on had a demonstrated LockHeld incident (tombstone-box-000368-aa4d16e2), and merged review-lock-only-for-intake fixed it. Serve no longer runs triage on its own (serve-no-auto-triage merged), so triage holds the lock only when an operator runs it on demand. That is speculative hardening for now.

- Message class suggestion, origin session, no stage/outcome/report attached
- Proposal is conditional on an unbuilt prerequisite: a dedicated journal-append lock
- declined-box-000381-d5f2e361 declined the general 'no lock across model calls' rule; review-lock-only-for-intake already fixed the review case
- tombstone-box-000368-aa4d16e2 shows the review lock problem had a concrete LockHeld incident; no equivalent incident is cited for triage
- serve-no-auto-triage merged: triage runs only on operator demand

Message: box-000385-d25d79d3
