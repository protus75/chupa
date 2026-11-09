---
id: declined-box-000165-b98fb360
kind: declined
link: box-000165-b98fb360
reopen_after_days: 90
---
A bootstrap note found that the frozen plan disagrees with itself about a diagnosis verdict outside the allowed set. Section 11.3 calls it a mechanical RMA to the Reject queue, while section 5 invariant 2 re-prompts a schema-invalid verdict first, and neither says which closed verdict the mechanical record carries. The code (`spine-diagnosis`) records `abandon-human` with a `mechanical` reason once the re-prompts run out. The note asks for section 11.3 to say so.

This is only a wording gap in the plan. `CHUPA_PLAN.md` is a frozen bootstrap record that is never edited, so the requested edit is not allowed. The note itself says the code already picks a closed verdict (`abandon-human`) after the re-prompts run out, so the engine does not have to guess at runtime. The note shows no wrong runtime behavior. Registry records 000100, 000111 and 000164 declined plan-wording reconciliations of the same kind.

- The message describes a mismatch between the wording of plan sections 11.3 and 5 and asks only for plan text to be pinned.
- The message says `spine-diagnosis` already records `abandon-human` with `mechanical: "no schema-valid verdict (<outcome>)"`, so runtime routing is set in code.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Earlier declines of plan-wording notes: declined-box-000100-ea74a111, declined-box-000111-aa8bb4fa, declined-box-000164-c54142c4.

Message: box-000165-b98fb360
