---
id: declined-box-000150-fd4c661b
kind: declined
link: box-000150-fd4c661b
reopen_after_days: 90
---
A bootstrap note said `runner.run_ticket` journals its `running` transition without `ticket_sha`. Because the drain's premise park keys on that field, a `premise_failed` from `run <stem>` would be released and offered again by the next drain. Current code already records the SHA: `chupa/runner.py:501-502` resolves `main:tickets/<stem>/ticket.md` and appends `{"to": "running", "ticket_sha": ticket_sha}`.

The gap the note describes is already closed in current code. `run_ticket` journals `ticket_sha` in its `running` transition, the same way the drain (`chupa/drain.py:513`) and serve (`chupa/serve.py:154`) do. The premise park in `chupa/drain.py:73` can therefore key a park from `run` on the ticket's blob, so the behavior the note reports cannot happen today.

- chupa/runner.py:474 defines run_ticket
- chupa/runner.py:501 resolves ticket_sha = rev_parse(main:tickets/<stem>/ticket.md)
- chupa/runner.py:502 appends STATE_TRANSITION {to: running, ticket_sha: ticket_sha}
- chupa/drain.py:513 and chupa/serve.py:154 journal the same body shape
- chupa/drain.py:73 reads ticket_sha from the running body for the premise park

Message: box-000150-fd4c661b
