---
id: tombstone-box-000241-931e0cd7
kind: tombstone
link: declined-box-000111-aa8bb4fa
reopen_after_days: 90
---
The frozen plan's section 9 says merge restores the worktree's ticket plane to main's content before the rebase. Restoring straight from main would stage main's newer lifted files against the older branch head, and git refuses a rebase with a dirty index. `chupa/merge.py` already restores from the branch head's own committed ticket plane, so the rebase ends on main's content. The note asks only for section 9 to name the branch head as the restore source.

Registry record declined-box-000111-aa8bb4fa already decided this same request: reword section 9 to name the branch head as the restore source. The code already does the right thing. The note asks only for plan wording, and the plan is frozen.

- declined-box-000111-aa8bb4fa describes the identical section 9 restore-source wording mismatch and the merge.py behavior
- The message reports no incorrect runtime behavior: merge.py restores from the branch's committed ticket plane
- CHUPA_PLAN.md is frozen and never edited, so a plan-wording change cannot be built as a ticket

Message: box-000241-931e0cd7
