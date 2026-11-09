---
id: tombstone-box-000239-b51a67dc
kind: tombstone
link: declined-box-000100-ea74a111
reopen_after_days: 90
---
This suggestion points out that the frozen plan and the code disagree about red Check results. The plan's section 5 invariant 2 says the driver re-prompts on a hard gate failure. In the code, Check is a separate mechanical stage after Implement: `specs/implement.md` declares `gates: []`, and a red Check ends as `gate_failed`. The note asks section 5 to say whether Check gates belong in Implement's driver loop or come back only through the drain's re-offer, which feeds the findings in.

Registry record declined-box-000100-ea74a111 already covers this exact request. It names the same section 5 invariant 2 conflict, the same `gates: []` declaration, the same `gate_failed` terminal and the same two choices for section 5. That record declined it because only the plan wording is wrong. The engine has no wrong runtime behavior here, and the frozen plan is never edited.

- declined-box-000100-ea74a111 describes the same section 5 invariant 2 versus separate-Check-stage mismatch and asks the same question.
- CLAUDE.md says CHUPA_PLAN.md is a frozen bootstrap design record and is never edited, so a request to reword a plan section cannot become a ticket.
- The message reports no failed run caused by Check running as its own stage. Findings already reach the next attempt through the drain's re-offer.

Message: box-000239-b51a67dc
