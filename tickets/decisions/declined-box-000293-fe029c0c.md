---
id: declined-box-000293-fe029c0c
kind: declined
link: box-000293-fe029c0c
reopen_after_days: 60
---
A retro finding about Phase 6 continuation seeding. Four times in a row (phase6-continue-02 to -05), Implement returned premise_failed spec_gap naming only the first missing 19.P6 entry unit, so four separate plan-gap tickets were needed (plan-gap-35, 37, 40, 41). It proposes that specs/implement.md require one spec_gap finding for every absent or under-specified unit in the eligible set.

The machinery this finding depends on has since been removed, so the behavior can no longer happen. The merged tickets remove-seeding, remove-plan-grammar, remove-plan-gap-hardening, remove-phase-exits and prompts-drop-plan took out phase continuation seeding, plan entry units and plan-gap hardening. The current chupa/specs/implement.md has no spec_gap kind and no registry or entry-unit eligible set, so the proposed rule would have nothing to apply to. The general case, a premise_failed that names only the first problem, is already covered by the merged implement-all-premise-findings ticket: implement.md now tells the model to work through every forced file and report each one as its own finding, never stopping at the first. There is no reachable harmful behavior left to repair.

- grep of chupa/specs/implement.md finds no 'spec_gap' and no entry-unit or eligible-set language; premise findings are all coded 'premise' (lines 57-60, 98-104)
- implement.md line 59: 'Before replying `premise_failed` for a scope reason, work the change through ...' (added by merged ticket implement-all-premise-findings, which reports every finding instead of only the first)
- Merged stems include remove-seeding, remove-plan-grammar, remove-plan-gap-hardening, remove-phase-exits, prompts-drop-plan
- phase6-continue-02 through -08 and phase6-exit are all merged; the Phase 6 chain the finding describes is finished

Message: box-000293-fe029c0c
