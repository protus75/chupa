---
id: declined-box-000177-61a7474f
kind: declined
link: box-000177-61a7474f
reopen_after_days: 90
---
A bootstrap handoff note warned that ticketless triage calls would share one LLM effect key, and so replay each other's results, if `Driver.run` always took `run_seq` from the journal. It said the merged `box-triage` work added a `run_seq` override for ticketless calls, and it asked the frozen plan (section 6 or 19.P2) to describe that override.

The runtime gap the note describes is already closed. `Driver.run` takes a `run_seq` override, refuses it when a ticket is given, and uses it in place of the journal value. Triage passes the box message's sequence number as that override, so two messages in one pass get different keys. What remains is a request to reword `CHUPA_PLAN.md`, which is a frozen record and is never edited. No reachable wrong behavior is left.

- chupa/driver.py:194 `Driver.run` accepts `run_seq: int | None = None`
- chupa/driver.py:257-259: `run_seq` requires `ticket=None`, and `seq = run_seq if run_seq is not None else journal_run_seq(...)`
- chupa/triage.py:321 passes `run_seq=message.seq`, so each box message gets its own key
- `box-triage` is merged
- The project rules say `CHUPA_PLAN.md` is frozen and never edited

Message: box-000177-61a7474f
