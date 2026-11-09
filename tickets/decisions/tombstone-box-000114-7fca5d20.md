---
id: tombstone-box-000114-7fca5d20
kind: tombstone
link: outbox-lift-named-artifact-only
reopen_after_days: 30
---
If a branch commits a file inside its own `tickets/<stem>/` outbox, the scope fence lets it through. `lift_outbox` then copies that file to main before the rebase, so `post_rebase_regate` never sees it in the branch diff. The note asks whether the lift should skip tracked files or Check should refuse committed outbox files.

The harm here is that unvetted files under a ticket's outbox reach main through the lift with no gate in between. The open ticket `outbox-lift-named-artifact-only` already fixes that. It limits each lift to the one artifact the engine names (`run.md`, `review.md`, `checks.json`/KNOWN_ARTIFACTS, or `only`), skips symlinks and scrubs the content. Once it lands, any other file the branch commits under its outbox is not lifted. That file stays in the branch diff where the rebase regate can see it. Only engine-named artifacts can still be lifted, and the engine rewrites those itself. The note offers no incident beyond the two design options it raises.

- chupa/stages.py:342-353 `_lift_files` picks every file under the worktree outbox except `ticket.md`, filtered only by `only`, the KNOWN_ARTIFACTS/kind rule and byte equality; it does not check whether the file is tracked
- tickets/outbox-lift-named-artifact-only/ticket.md Goal: the lift commits outbox files to main with no scope fence, Review or Redactor; Scope in: each lift commits only the artifact the engine names for it
- chupa/stages.py:375-376 `dirty_code` leaves the stem's outbox (except `ticket.md`) out of the dirty-code check, which is why outbox files pass the fence

Message: box-000114-7fca5d20
