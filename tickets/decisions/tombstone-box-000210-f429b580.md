---
id: tombstone-box-000210-f429b580
kind: tombstone
link: declined-box-000035-b9c95daa
reopen_after_days: 90
---
The note says `DEFAULT_GATE_SEVERITY` in `chupa/gates.py` makes every engine gate code hard at merge, including `bug_evidence` and `core_drift`. The frozen plan puts both gates in Phase 6 and leaves `core_drift` out of the section 7 v1 hard set. It asks the plan to say whether the all-hard default covers the whole engine vocabulary or only the v1 hard set.

This repeats registry record declined-box-000035-b9c95daa: the same gates, the same all-hard default and the same request for plan wording. The note also only asks for wording in a frozen plan and shows no wrong runtime behavior.

- Registry record declined-box-000035-b9c95daa already covers `DEFAULT_GATE_SEVERITY` making `bug_evidence` and `core_drift` hard against the section 7 v1 hard set, and it asks the same scope question.
- CLAUDE.md says `CHUPA_PLAN.md` is a frozen bootstrap design record that is never edited, so a request to change plan wording cannot become a ticket.

Message: box-000210-f429b580
