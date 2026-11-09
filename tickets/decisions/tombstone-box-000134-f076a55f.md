---
id: tombstone-box-000134-f076a55f
kind: tombstone
link: already-satisfied-settles
reopen_after_days: 90
---
The note says the journal records a no-op ticket as `to: already_satisfied` while frozen plan section 7 says it settles as `to: merged`, and that drain's `SETTLED` set accepts both forms. It asks to pick one journal form and remove the other from `SETTLED`.

Merged ticket `already-satisfied-settles` already decided this. It made `drive` write `to: already_satisfied` as the settled terminal, and it gave status, the `reject` verb and drain one shared definition of the settled states (`merged` and `already_satisfied`). Keeping both in `SETTLED` was deliberate, because `merged` and `already_satisfied` are different outcomes. The only remaining gap is the wording in the frozen `CHUPA_PLAN.md`, which is never edited. No incorrect runtime behavior has been shown.

- chupa/runner.py:215-216 journals `to: already_satisfied` with reason `already_satisfied`
- tickets/already-satisfied-settles/ticket.md Scope in: one definition of the settled states (`merged`, `already_satisfied`) shared by status, reject and drain
- CHUPA_PLAN.md is frozen; a mismatch in plan wording alone is not a runtime defect

Message: box-000134-f076a55f
