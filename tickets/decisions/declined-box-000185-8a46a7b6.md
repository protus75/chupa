---
id: declined-box-000185-8a46a7b6
kind: declined
link: box-000185-8a46a7b6
reopen_after_days: 180
---
A bootstrap seeding note says that frozen-plan prompts 14-16 never created a deliverable for per-command base-diff attribution, even though settled contracts in 19.P2 refer to it. Prompt 17 authored it as `verification-base-attribution`, which has merged. The note asks for 19.P2's deliverables list and prompt 16 to name it, so a regeneration from the plan would produce it again.

This is a plan-wording mismatch with no runtime harm. The deliverable exists in code as merged ticket `verification-base-attribution`. Seeding and plan-driven regeneration have since been removed (`remove-seeding` and `prompts-drop-plan` are merged), and `CHUPA_PLAN.md` is a frozen record that is never edited. Changing the plan text would not alter any current behavior.

- Merged stems include `verification-base-attribution`, so the deliverable already exists.
- Merged stems include `remove-seeding`, `prompts-drop-plan` and `remove-plan-grammar`, so the plan no longer drives regeneration.
- Project rules state that `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Registry records declined-box-000144, 000164 and 000170 declined similar requests to reconcile plan wording.

Message: box-000185-8a46a7b6
