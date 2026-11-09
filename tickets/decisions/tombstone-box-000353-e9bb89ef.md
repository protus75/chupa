---
id: tombstone-box-000353-e9bb89ef
kind: tombstone
link: steps-open-author-files
reopen_after_days: 30
---
The suggestion says Recent Steps rows for author and triage, which have no ticket, point at tickets/<surface>/ticket.md files that do not exist, and asks that triage rows open the Suggestion Box message instead. Current main already does this for both surfaces. The merged ticket steps-open-author-files made author rows open the box message, the authored ticket, or the declined record. The same branch in `snapshot` now sends triage rows to the box message, matched by run_seq.

The author half is the same request as merged ticket steps-open-author-files. Its acceptance criterion rules out any Author row path of `tickets/author/ticket.md`. The triage half is already fixed on main. In `chupa/observe.py:672-677`, the `if surface in ("author", "triage")` branch looks up the box message by `run_seq` for triage and sets `path` to the message's resolution link or its box file, or None when no message matches. Neither surface falls through to the `tickets/<stem>/ticket.md` fallback. No behavior gap is left.

- chupa/observe.py:672-677: author and triage rows look up the box message (author by attempt, triage by run_seq). The path is the resolution link if that file exists, otherwise the message's box file, otherwise None.
- chupa/observe.py:681-684: only rows for other surfaces that carry a stem fall back to tickets/<stem>/ticket.md
- tickets/steps-open-author-files/ticket.md:22-35: this merged ticket fixed the author rows that pointed at the nonexistent tickets/author/ticket.md
- tickets/vscode-triage-step/ticket.md:46 had recorded the triage tickets/triage/ticket.md path as a separate problem. Current code resolves it.

Message: box-000353-e9bb89ef
