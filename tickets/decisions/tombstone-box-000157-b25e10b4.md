---
id: tombstone-box-000157-b25e10b4
kind: tombstone
link: plan-contract-section-render
reopen_after_days: 30
---
A bootstrap note reported a crash in Implement. `implement_stage` passed canonical plan ids such as `11` to `resolve_plan_contract`. That function parsed each id again as a bullet and raised `PlanContractError`, so every ticket citing a numeric `section N` failed on its first Implement render. The note also wanted a test that renders the Implement prompt for such a ticket. The note seeded this fix as ticket `plan-contract-section-render`, which has since merged.

The note names its own repair ticket, `plan-contract-section-render`, and that stem is on the merged list. The defect has also become unreachable since then: the merged tickets `remove-plan-grammar`, `prompts-drop-plan` and `drop-plan-citations-1..3` removed plan citations from the prompt path. No open ticket or registry record covers anything left over, so this message duplicates the merged ticket.

- Message: 'Seeded as `plan-contract-section-render` (P0, first in the Phase 2 queue, `spine-caps` depends on it)'
- Merged stems include `plan-contract-section-render` and `spine-caps`
- Merged stems include `remove-plan-grammar`, `prompts-drop-plan`, `drop-plan-citations-1`, `drop-plan-citations-2`, `drop-plan-citations-3`

Message: box-000157-b25e10b4
