---
id: declined-box-000035-b9c95daa
kind: declined
link: box-000035-b9c95daa
reopen_after_days: 60
---
In `chupa/gates.py`, `DEFAULT_GATE_SEVERITY` makes every code in `ENGINE_GATE_CODES` hard, including `bug_evidence` and `core_drift`. The frozen plan puts both gates in Phase 6, and its section 7 v1 hard set does not list `core_drift`. The note asks for the plan text to say whether the all-hard default covers every engine gate code or only the v1 hard set.

The note points out a mismatch in the plan's wording, not a fault in how the engine behaves. `CHUPA_PLAN.md` is frozen and never edited, so the clarification it asks for cannot be made. Phase 6 has already merged: `core-drift-activation`, `core-drift-classifier`, `bug-evidence-intake` and `bug-gate-grammar` are all merged. Both gates are now live, so treating them as hard at merge matches how the engine works today. An operator who wants a softer gate can set `review.gate_severity`, which `gates.merge_severity` merges over the default. No evidence shows a hard `bug_evidence` or `core_drift` finding wrongly blocking a merge.

- chupa/gates.py:24-25 lists bug_evidence and core_drift in ENGINE_GATE_CODES
- chupa/gates.py:32 DEFAULT_GATE_SEVERITY = {code: 'hard' for code in ENGINE_GATE_CODES}
- chupa/gates.py:93 merge_severity applies operator overrides over the default
- merged: core-drift-activation, core-drift-classifier, bug-evidence-intake, bug-gate-grammar, phase6-exit
- CLAUDE.md: CHUPA_PLAN.md is a frozen bootstrap design record and is never edited

Message: box-000035-b9c95daa
