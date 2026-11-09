---
id: declined-box-000138-3ce33b66
kind: declined
link: box-000138-3ce33b66
reopen_after_days: 90
---
The note said tickets committed by a seeding ticket never got a `ticket_intake` journal event, so drain had no age for them and sorted them after older tickets of the same priority. That seeding lane no longer exists. Merged ticket `remove-seeding` took it out, and in current code only `chupa/tickets.py` intake and `chupa/author.py:330` write tickets, and both journal `ticket_intake`.

The path the note describes was removed, so the problem it reports cannot happen any more. The surviving authoring paths, hand intake and box author, both emit the event. That leaves no current behavior that causes harm and nothing for one ticket to fix.

- merged stem `remove-seeding`
- the only `ticket_intake` producers are `chupa/tickets.py:28` (INTAKE_SIGNAL) and `chupa/author.py:330`
- no seeding code path is left in `chupa/` (grep for `seeding` and `def seed` finds nothing)

Message: box-000138-3ce33b66
