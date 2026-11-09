---
id: declined-box-000090-aa1991da
kind: declined
link: box-000090-aa1991da
reopen_after_days: 90
---
In `chupa/tickets.py` intake, the ticket commit and the `ticket_intake` journal signal are written one after the other (line 687, then line 689). The author path in `chupa/author.py:330` does the same. If the process crashes between the two writes, the ticket stays committed with no intake signal, and nothing adds the signal later. The note asks whether the signal matters and, if it does, for a reconcile from `git log` at startup.

The signal is not needed to schedule the ticket. Its only readers are `drain.authored_at`, which sets age order within a priority, `status.py`, which projects intake rows, and `stats.py`, which counts intake. A ticket that is missing the signal still gets picked, run and merged. It only sorts after the other tickets at its priority and is left out of the intake counts. That needs a crash in a window of a few milliseconds and has never been seen. The harm is a small ordering and reporting error, so a recovery path is speculative hardening.

- chupa/tickets.py:687-689 runs `git.commit` and then `journal.append(SIGNAL ticket_intake)`
- chupa/drain.py:99-111 `authored_at` and `sort_key`: a stem with no intake signal sorts last within its priority and is still picked
- chupa/status.py:63 and chupa/stats.py:66,144 read the signal for intake projection and counts only
- chupa/author.py:330 has the same commit-then-signal sequence

Message: box-000090-aa1991da
