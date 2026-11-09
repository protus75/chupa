---
id: declined-box-000117-cdc4c20b
kind: declined
link: box-000117-cdc4c20b
reopen_after_days: 90
---
Inside `write_squash` (`chupa/merge.py:325-334`), a crash can land after `merge --squash` stages the branch on main but before `commit` runs. Main's index then holds staged changes, and the note asks for reconcile or a tree-hash check to find that state and reset it on its own. In current code, a replay first runs `dirty_overlap` (`chupa/merge.py:251-270`, called at line 311). It sees staged paths that overlap the branch diff and refuses with a `dirty_checkout` finding that carries a paved road, so `merge --squash` never runs into the dirty index. Nothing resets the index automatically.

The crash window this note describes is already caught and stopped safely: the merge-dirty-checkout gate refuses before squashing again and leaves main untouched. What remains is that a person has to clean the index, with no automatic recovery. That is a hardening request for a narrow crash window. No incident is cited and no wrong runtime result is shown. Decision declined-box-000116-f4ed6b34 already declined the matching crash window between commit and journal for the same reason. Reopen if a real crash leaves a staged half-squash on main, or if the `dirty_checkout` paved road ('commit or revert') leads an operator to commit a squash without trailers.

- chupa/merge.py:311 runs dirty_overlap before write_squash
- chupa/merge.py:251-270 finds tracked non-untracked changes that overlap the branch diff and returns a dirty_checkout finding with a paved road
- chupa/merge.py:330-331 run merge_squash and commit back to back inside the merge effect
- chupa/reconcile.py has no squash or index recovery
- Related decision: declined-box-000116-f4ed6b34 (adjacent crash window inside write_squash)

Message: box-000117-cdc4c20b
