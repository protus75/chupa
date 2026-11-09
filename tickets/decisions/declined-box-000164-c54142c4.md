---
id: declined-box-000164-c54142c4
kind: declined
link: box-000164-c54142c4
reopen_after_days: 90
---
A bootstrap note found that the frozen plan's diagnosis context (section 11.3) names a "capped diff", but the diagnosis-eval case envelope (section 19.P2) has no diff field. The note says `spine-diagnosis` already passes the harvest's `diff_stat` as that diff, so the eval cases and the production calls see the same material. It asks for that reading to be written into section 11.3, or for a diff field to be added to the eval envelope.

This is a mismatch in the plan's wording, not a behavior gap. The note itself says `spine-diagnosis` already uses `diff_stat` in both production and eval, so the two inputs agree and nothing incorrect happens at runtime. `CHUPA_PLAN.md` is a frozen design record that tickets never edit, so the requested change to section 11.3 cannot be made. Earlier plan-wording notes were declined for the same reason (000015, 000050, 000102, 000111, 000144).

- The message says `spine-diagnosis` renders the harvest's `diff_stat` as the capped diff, so production and eval material match.
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.
- Plan-wording mismatches were declined before: declined-box-000015, 000050, 000102, 000111, 000144.

Message: box-000164-c54142c4
