---
id: declined-box-000140-2e5df53a
kind: declined
link: box-000140-2e5df53a
reopen_after_days: 90
---
The drain loop in `chupa/drain.py` reads and folds the whole journal several times on each iteration: in `run` (lines 349, 356, 394, 417), in `_run_one`'s re-offer and terminal lookups (lines 511, 524), and in the parked-stem and state folds (lines 591, 653). The cost grows with journal events times dispatches. The suggestion is to fold once per iteration and pass the result through.

This is a speculative performance change, and the note itself makes it conditional on the cost becoming measurable. It reports no incorrect runtime behavior, no measured slowdown or timeout, and no failed drain. Each iteration does only a few full reads, and one provider call takes far longer, so there is no demonstrated harm for a ticket to fix.

- chupa/drain.py:349,356,394,417: `run` calls `self.c.journal.read()` several times per iteration
- chupa/drain.py:511,524: `_run_one` reads the full journal again for the re-offer record and the terminal transition lookup
- chupa/drain.py:591,653: more full-journal folds for the latest states and the terminal body
- The message gives no measured latency, journal size, or failure; it is conditioned on 'when journal size makes this measurable'

Message: box-000140-2e5df53a
