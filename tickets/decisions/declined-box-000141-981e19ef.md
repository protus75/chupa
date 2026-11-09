---
id: declined-box-000141-981e19ef
kind: declined
link: box-000141-981e19ef
reopen_after_days: 90
---
The drain's `_scan` in `chupa/drain.py` checks committed tickets with `parse_ticket` and then runs its own cycle scan over the open set. `run` uses `validate_ticket` in `chupa/tickets.py`, which is `parse_ticket` followed by checks for `Depends on` and `Runs before` cycles across the repo graph. The note proposes one shared admission check for `run` and `drain` so the two cannot drift apart.

This is a hardening and refactor proposal, and it shows no current harm. Both paths use the same `parse_ticket` grammar. Every committed ticket already passed `validate_ticket` at intake or authoring before it reached the ticket plane. The note names no ticket that one path admitted and the other refused, and no wrong dispatch, crash or stuck queue. A drift that has not happened yet is speculative, and the admission bar requires current incorrect behavior at runtime.

- chupa/drain.py:426 `_scan` calls `parse_ticket(stem, path.read_text(), repo)` on committed, unsettled ticket files and records `TicketInvalid` findings as invalid
- chupa/tickets.py:518-529 `validate_ticket` = `parse_ticket` + Depends on / Runs before cycle checks via `depends_cycle`
- Both admission paths share the same grammar function, so only the cycle check runs differently
- The message's origin is bootstrap-ingest with no stage, outcome or incident attached

Message: box-000141-981e19ef
