---
id: tombstone-box-000259-c6293ec4
kind: tombstone
link: plan-contract-section-render
reopen_after_days: 90
---
Implement passed already-canonical plan ids (for example `11` from `section 11`) to `resolve_plan_contract`. That function parsed each id again as a bullet and raised `PlanContractError`, so any ticket citing a numeric plan section failed on its first Implement render. The note also asked for a test that renders Implement for such a ticket. Merged ticket `plan-contract-section-render` fixed the crash, and plan grammar and contracts have since been removed.

This message says the same thing as merged ticket `plan-contract-section-render`, which the message itself names as the seeded fix. Registry record tombstone-box-000157-b25e10b4 already tombstoned an identical note against that ticket. Later merged tickets (`remove-plan-grammar`, `prompts-drop-plan`, `drop-plan-citations-*`) removed plan-contract rendering, so the failure cannot happen in current code.

- Merged stems include `plan-contract-section-render`.
- Decision registry `tombstone-box-000157-b25e10b4` links the same report to `plan-contract-section-render`.
- Merged stems `remove-plan-grammar`, `prompts-drop-plan` and `drop-plan-citations-1..3` removed plan-contract citations from the render path.

Message: box-000259-c6293ec4
