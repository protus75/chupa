---
id: tombstone-box-000254-bc04b037
kind: tombstone
link: declined-box-000138-3ce33b66
reopen_after_days: 90
---
The note says a ticket committed by a seeding ticket gets no `ticket_intake` journal event. Drain therefore has no age for it and sorts it after aged stems of the same priority. The note asks the seeding lane to journal that event. Registry record 000138 already decided this request.

This is the same gap as record declined-box-000138-3ce33b66. That record declined it because merged ticket `remove-seeding` took the seeding lane out, so the authoring path the note names no longer exists. Per that record, only `chupa/tickets.py` intake and `chupa/author.py` write tickets, and both journal `ticket_intake`.

- Decision registry declined-box-000138-3ce33b66 covers the same seeding-lane `ticket_intake` gap
- Merged stems include `remove-seeding`
- Message origin is `bootstrap-ingest`, so the note predates the seeding lane's removal

Message: box-000254-bc04b037
