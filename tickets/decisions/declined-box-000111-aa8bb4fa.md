---
id: declined-box-000111-aa8bb4fa
kind: declined
link: box-000111-aa8bb4fa
reopen_after_days: 90
---
A bootstrap note says section 9 of the frozen plan tells merge to restore the worktree's `tickets/**` to main's content before rebasing. Restoring literally from `main` would stage main's newer lifted files against the older branch head, and git refuses to rebase with a dirty index. `chupa/merge.py` restores from the branch's own committed ticket plane, so the rebase still ends on main's content. The note asks only to reword section 9 so it names the branch head as the restore source.

This is a mismatch between the plan's wording and the code, with no runtime fault. The note itself says merge.py already restores from the branch head and the rebase succeeds. CHUPA_PLAN.md is a frozen design record that tickets never edit, so the rewording it asks for cannot be built as a ticket.

- The message says merge.py restores from the branch's committed ticket plane, so the rebase lands on main's content and nothing fails.
- The only change proposed is rewording section 9 of the plan.
- CLAUDE.md: CHUPA_PLAN.md is frozen and never edited.
- Similar plan-wording notes were declined: declined-box-000015-14c41885, declined-box-000102-56449adb.

Message: box-000111-aa8bb4fa
