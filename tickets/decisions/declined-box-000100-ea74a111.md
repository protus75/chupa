---
id: declined-box-000100-ea74a111
kind: declined
link: box-000100-ea74a111
reopen_after_days: 90
---
The note points out that the frozen plan's section 5 invariant 2 says the driver re-prompts on a hard gate failure. In the code, Check is a separate mechanical stage after Implement: `specs/implement.md` declares `gates: []`, and a red Check ends as `gate_failed` instead of re-prompting the same Implement workspace. The note asks section 5 to say whether Check gates belong in Implement's driver loop or only re-enter through the drain's findings-fed re-offer.

This is a mismatch between the plan's wording and the code, not a behavior gap. `CHUPA_PLAN.md` is frozen and never edited, so the requested change cannot be made. The note shows no incorrect runtime behavior: a red Check already ends cleanly as `gate_failed`, and the drain re-offers the ticket with the findings, which merged tickets serve-reoffer-dispatch and serve-reoffer-rule cover. No ticket stalls, no cap is lost, and no bad work merges.

- The message asks for wording in plan section 5 to be settled. It reports no failed run or wrong outcome.
- CLAUDE.md: 'The plan is the seed. `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.'
- The note itself says a red Check is a stage terminal (`gate_failed`) and Implement declares `gates: []`. That is a consistent design.
- Merged stems serve-reoffer-dispatch and serve-reoffer-rule already provide the findings-fed re-offer path the note describes.

Message: box-000100-ea74a111
