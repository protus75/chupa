---
id: declined-box-000103-1735c1ac
kind: declined
link: box-000103-1735c1ac
reopen_after_days: 90
---
A bootstrap note says Implement and Review resolve reasoning effort from different places. Implement uses the ticket's `agent_effort`. Review uses the `effort` declared in `specs/review.md`, at the ticket's tier. The note asks section 6 of the plan to state, for each surface, where its effort comes from.

This asks for a change to the wording of the frozen bootstrap plan (`CHUPA_PLAN.md` is never edited). It does not show a runtime fault: the note describes the current behavior as the intended baseline and points to no wrong effort used at runtime or any harm from the split. Without a reachable misbehavior, it does not meet the bar for a ticket.

- The message class is `suggestion` with origin `bootstrap-ingest`, and it has no stage, outcome, or failure report.
- The request is to pin effort resolution in plan section 6. That is a documentation change to a plan the project treats as frozen.
- The note calls Review's spec-declared effort the measured baseline, so the split is intentional and not a defect.
- No open or merged ticket covers this. The only related open ticket, `codex-effort-closed-lookup`, is about codex rejecting the `max` effort, which is a different problem.

Message: box-000103-1735c1ac
