---
id: tombstone-box-000245-f746a086
kind: tombstone
link: declined-box-000122-6f939062
reopen_after_days: 90
---
This bootstrap note says that when `drive` reaches a non-ok terminal state, it journals the outcome and stage and leaves the ticket worktree on disk, because before harvest existed the worktree was the only evidence. It asks the frozen plan's section 11.2 handler order, which ends with "wipe worktree", to say whether the Phase 1 terminal wipes the worktree before harvest exists.

This note asks the same question as registry record declined-box-000122-6f939062: should the Phase 1 non-ok terminal wipe the worktree before harvest exists? That record already declined it. The question is also out of date: spine-harvest has merged, and record 000162 says harvest now wipes the worktree at every non-ok terminal.

- Registry record declined-box-000122-6f939062 covers the same question about the `drive` non-ok terminal and the section 11.2 wipe order.
- Merged ticket spine-harvest added harvest before the wipe.
- Registry record declined-box-000162-f08b3262 says harvest now wipes the worktree at every non-ok terminal.

Message: box-000245-f746a086
