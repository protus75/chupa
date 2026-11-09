---
id: declined-box-000336-df859295
kind: declined
link: box-000336-df859295
reopen_after_days: 30
---
`chupa status` builds its view only from the journal, so a `tickets/<stem>/ticket.md` that exists in the working tree but has not been committed by intake does not appear anywhere in its output. The suggestion asks for an 'awaiting intake' section listing those files, after `box-declined-verdict` sat uncommitted and unseen on 2026-11-07.

This asks for more visibility, not a fix for wrong runtime behavior. `status` is meant to be a journal-only projection: its intake block lists `ticket_intake` signals, and it does not scan the disk. An uncommitted ticket is not dispatched wrongly, lost, or corrupted. It waits until intake runs, and drain and serve run intake on every loop. The one incident cost some delay, but `box-declined-verdict` is now merged, so nothing is still harmed. If the file stayed uncommitted because intake refused it, the case is the one already decided in declined-box-000093-e1f5e684 and tombstone-box-000094-deddbd70 (refused or unparseable stems are not shown in status, and a read-only disk scan was proposed). Adding a working-tree scan to `status` would be new projection scope that one delay does not justify.

- chupa/status.py:63 builds `intake` only from journal `ticket_intake` signals; status reads no working-tree or porcelain state
- chupa/status.py:126 renders the intake block from that journal tuple only
- box-declined-verdict is in the merged set, so the reported uncommitted ticket did land
- declined-box-000093-e1f5e684 and tombstone-box-000094-deddbd70 already decided the request for status to show on-disk tickets intake did not commit (refused or unparseable)
- drain-intake-each-loop is merged: background loops run intake on every iteration, so an eligible uncommitted ticket only waits for the next loop

Message: box-000336-df859295
