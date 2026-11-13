---
id: declined-box-000430-3198bbf4
kind: declined
link: box-000430-3198bbf4
reopen_after_days: 60
---
Requisition review approved serve-live-verdicts, whose Scope out left drain deciding every confirm/reject request stale while serve applied them. The note asks requisition review to snag any Scope out that leaves an operator verb served by one engine verb but not by another.

Only one incident is cited, and its harm is already fixed. The merged ticket drain-settles-admissions makes drain settle verdict requests through the shared apply path, both between tickets and while one runs, and removes the 'drain decides them stale' wording from docs/how-chupa-works.md section 7.3. Even before that fix, the gap was not a hold with no release: the operator could stop the drain and confirm through the lock-free path or under serve. The Scope out was a deliberate split that a follow-up ticket closed. The message shows no second ticket where this pattern harmed a run, so a new requisition-review rule would be speculative hardening of chupa/specs/requisition_review.md. Reopen if requisition review approves another ticket whose Scope out leaves an operator verb refused or decided stale under one running engine verb while another serves it, and that gap costs a run or strands an operator action.

- tickets/serve-live-verdicts/ticket.md:41 Scope out: 'drain consuming verdict requests. A request published while drain runs is decided stale as today'
- tickets/drain-settles-admissions/ticket.md:36 makes chupa/drain.py call consumer.inbox.settle_admissions in _await_controlled and the between-ticket checkpoint
- drain-settles-admissions and serve-live-verdicts are both in the merged set
- grep for 'stale' in chupa/drain.py finds no stale-verdict path on current main
- No open ticket or registry record shows a second instance of a Scope out leaving a verb unservable under one engine

Message: box-000430-3198bbf4
