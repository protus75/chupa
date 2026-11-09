---
id: declined-box-000380-fd7d9e73
kind: declined
link: box-000380-fd7d9e73
reopen_after_days: 30
---
Row 20 of the verb table in docs/host-running.md still says serve accepts a queued retro request but does not run it. That has been out of date since retro-request-serve merged: chupa/serve.py now runs both requested and due retros at idle points (retro_pending, check_retro, run_retro). The suggestion is to fix that one table row.

The mismatch is real: the doc row is out of date and serve does run queued retros. But it only affects documentation. The retro verb, serve's handling of the request, and the tests that pin the verb table all behave correctly. No reachable runtime path gives a wrong result, and no operator decision is shown to have gone wrong because of the row. A doc wording fix with no tied runtime harm does not meet the author bar. No open ticket covers this row. vscode-venv-default touches docs/host-running.md only about how chupa is invoked.

- docs/host-running.md:20: '| `retro` | Yes | Run a retro report now, or queue one on the running engine (serve accepts it but does not yet run it). |'
- chupa/serve.py:336-355: retro_pending() checks the control projection's retro_id against served_retro_id, and check_retro/run_retro build and run a Retro
- merged stem retro-request-serve shipped serve-side retro execution and did not update the host-running.md row

Message: box-000380-fd7d9e73
