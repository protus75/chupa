---
id: declined-box-000410-feb371d1
kind: declined
link: box-000410-feb371d1
reopen_after_days: 14
---
If Implement returns premise_failed and Diagnose overrules it with a retry verdict, the drain still holds the stem until someone edits its committed ticket.md. Nobody knows an edit is needed, so the stem sits idle and the drain goes quiescent. This happened to journal-incremental-read attempt 1 on 2026-11-11.

This repeats ticket premise-overruled-escalates, which is confirmed and on disk at tickets/premise-overruled-escalates/ticket.md but not yet committed through intake. That ticket names the same cause: chupa/drain.py::parked_blob holds every premise_failed stem until ticket.md changes, whatever the dispatch. It cites the same incident (journal-incremental-read attempt 1, 2026-11-11). It covers the requested repair: an Implement premise_failed that Diagnose overrules with retry is routed as escalate through next_rung, re-offered without a ticket edit, and carries Diagnose's lessons. At the top rung, or once caps are spent, it goes to the Reject queue. Reopen if that ticket is rejected or abandoned without merging, or if a retry-dispatched premise_failed still parks after it merges.

- tickets/premise-overruled-escalates/ticket.md Goal / Why: parked_blob holds every premise_failed stem until ticket.md changes, whatever the dispatch; journal-incremental-read attempt 1 on 2026-11-11 (evidence/premise-retry-parked.txt)
- chupa/drain.py:85 parked_blob returns ran_sha for any last terminal whose to is premise_failed and never checks body.dispatch; only an operator keep clears it (lines 76-84)
- tickets/premise-overruled-escalates/ticket.md Scope in: runner.py routes an Implement premise_failed with Diagnose verdict retry as escalate, and parked_blob holds nothing for dispatch escalate
- unresolvable link: premise-overruled-escalates

Message: box-000410-feb371d1
