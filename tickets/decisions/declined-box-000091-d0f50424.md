---
id: declined-box-000091-d0f50424
kind: declined
link: box-000091-d0f50424
reopen_after_days: 60
---
When ticket intake sees a staged rename of a ticket file, it keeps only the new path. The deletion of the old path goes through without any check, so a stem that other tickets depend on can disappear unnoticed.

In `chupa/tickets.py`, `_porcelain` keeps only the new side of a rename, and `_pending` skips every staged or worktree deletion. A plain `D` deletion of a depended-on ticket is therefore just as unchecked as the old side of a rename. Intake never checks deletions, so this is not a rename bug. It is the existing policy of not linting deletions. The note cites no incident where a removed stem broke a dependent ticket or blocked the queue, and it gives no measurable harm. Adding a deletion check would be speculative hardening.

- chupa/tickets.py:574-575 `_porcelain` replaces a rename entry with its new path only
- chupa/tickets.py:584-585 `_pending` skips any entry whose status has `D` in either column, so plain deletions are not linted either
- The message has origin bootstrap-ingest and cites no run that failed because a depended-on stem vanished

Message: box-000091-d0f50424
