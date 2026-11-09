---
id: declined-box-000284-2e8cd5af
kind: declined
link: box-000284-2e8cd5af
reopen_after_days: 90
---
A retro finding says that a spec_gap finding could only name a plan unit the ticket already cited. When a successor entry unit was missing, the finding was pinned to a nearby cited unit (phase6-continue-02 named 19.P6.fixture-host-scaffold instead of the missing 19.P6.bug-gate-grammar and 19.P6.report-inbox-triage). Hardening then fenced plan-gap-28 to the wrong unit, and both tickets ended in the Reject queue. It proposes that a spec_gap name the missing registry row's entry unit id even when the ticket does not cite it.

The failure path no longer exists. The plan-unit machinery has been removed by the merged tickets remove-plan-gap-hardening, remove-seeding, remove-plan-grammar, prompts-drop-plan and plan-off-serve-path. The two specs the proposal would edit, chupa/specs/requisition_review.md and chupa/specs/implement.md, no longer mention spec_gap, plan units, entry units or registry rows. Nothing creates a plan-gap hardening ticket fenced to a cited unit anymore, so no current runtime behavior is wrong and no measurable repair is possible. The two units the finding called missing, bug-gate-grammar and report-inbox-triage, have since merged.

- Grep of chupa/specs for 'spec_gap|unit' finds no spec_gap, entry-unit or registry-row instruction in requisition_review.md or implement.md
- chupa/artifacts.py:39-45 keeps Finding.kind 'spec_gap' with a unit field, but no prompt spec asks for it
- chupa/journal.py:35 keeps spec_gap_hold only so historical terminals are still recognized
- Merged stems include remove-plan-gap-hardening, remove-seeding, remove-plan-grammar, prompts-drop-plan, plan-off-serve-path, bug-gate-grammar and report-inbox-triage

Message: box-000284-2e8cd5af
