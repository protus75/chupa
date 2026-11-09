---
id: declined-box-000144-c67434f6
kind: declined
link: box-000144-c67434f6
reopen_after_days: 90
---
A bootstrap review note says the frozen plan's prompt 11/12 text describes re-entry as a drain-side render seam (`drain.Reentry`/`no_reentry`). The shipped diff removed that seam and renders re-entry inside `stages.implement_stage`. The note asks for the plan text to be changed to match where re-entry now lives.

This is only a mismatch between the plan's wording and the code. The note itself says the shipped re-entry works, so no runtime behavior is wrong. Also, `CHUPA_PLAN.md` is a frozen bootstrap design record that is never edited, so the requested change goes against project policy. Decisions 000015, 000100 and 000111 declined similar plan-wording requests.

- The message says the change 'works'; it asks only to align plan prose.
- CLAUDE.md: 'The plan is the seed. CHUPA_PLAN.md is a frozen bootstrap design record and is never edited.'
- Matching earlier declines of plan-wording-only notes: declined-box-000015-14c41885, declined-box-000100-ea74a111, declined-box-000111-aa8bb4fa.

Message: box-000144-c67434f6
