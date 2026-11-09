---
id: declined-box-000174-123d065d
kind: declined
link: box-000174-123d065d
reopen_after_days: 90
---
A bootstrap handoff note says frozen-plan section 11.4 lets an auto-keep fire when "the retry cap still holds budget". A machine keep never re-arms a spent cap, though, so auto-keeping a stem whose infra, diagnosis or premise_bounce cap is spent would re-offer nothing. The merged `escalation-ladder` code auto-keeps only when `spent(...)` returns None, meaning every cap still has budget. The note asks for section 11.4 to state that reading.

This asks for plan wording only. The note itself says the shipped `escalation-ladder` code already auto-keeps only when every cap holds budget, so the runtime does nothing wrong. `CHUPA_PLAN.md` is a frozen design record that is never edited. A mismatch between plan wording and the code is declined unless it causes incorrect behavior at runtime.

- The note says `escalation-ladder` auto-keeps only when `spent(...)` is None, meaning every cap holds budget.
- `escalation-ladder` is a merged stem.
- Project rules say `CHUPA_PLAN.md` is frozen and never edited.
- The note reports no run where a spent cap was auto-kept.

Message: box-000174-123d065d
