---
id: declined-box-000161-5d0ba4ad
kind: declined
link: box-000161-5d0ba4ad
reopen_after_days: 90
---
A bootstrap review note says the seed lint required ticket `plan-contract-section-render` to cite a phase-unit (`19.P2`). The resolver it fixed was a `19.P0` deliverable, so the citation named the wrong owning unit only to pass lint. The note's complaint is about the rule that made a bug-fix seed cite a phase unit.

The rule behind this note no longer exists. Merged tickets `remove-seeding`, `remove-plan-grammar`, `drop-plan-citations-1..3`, `prompts-drop-plan` and `remove-phase-exits` removed seeding and the plan-citation grammar, so no current lint forces a ticket to cite a phase unit. The affected ticket `plan-contract-section-render` has also merged. Even before that, the wrong citation was a metadata mismatch with no reachable incorrect runtime behavior.

- Merged stems include remove-seeding, remove-plan-grammar, drop-plan-citations-1, drop-plan-citations-2, drop-plan-citations-3, prompts-drop-plan, remove-phase-exits.
- Merged stems include plan-contract-section-render, the ticket the note is about.
- Decision declined-box-000086-6a71f798 records that phase exits and seeding were removed and the engine no longer parses plan-bound sections.
- Decision tombstone-box-000157-b25e10b4 records that the resolver fix itself merged.

Message: box-000161-5d0ba4ad
