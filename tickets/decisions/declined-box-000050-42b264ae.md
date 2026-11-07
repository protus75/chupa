---
id: declined-box-000050-42b264ae
kind: declined
link: box-000050-42b264ae
reopen_after_days: 90
---
Section 8 of the frozen plan names only the quoted `[chupa-data:` form. It never states the raw data-block delimiter or the begin/end line grammar that `chupa/specs.py` builds from parts as `DATA_DELIM`. The note asks the plan to state that grammar so a regeneration from the plan would reproduce it.

This is a wording gap in the plan, not a runtime defect. The delimiter grammar is defined once, in `chupa/specs.py`, and every prompt renders through that constant, so nothing currently behaves incorrectly. `CHUPA_PLAN.md` is a frozen bootstrap record that is never edited, and the bootstrap regeneration path the note relies on has been removed (`remove-bootstrap-ingest`, `remove-plan-grammar`, `prompts-drop-plan`). Nothing measurable would change after an edit.

- The message cites no failing run, malformed prompt or parse error. It names only a missing plan statement.
- Project rules say `CHUPA_PLAN.md` is frozen and never edited, and that current docs describe the code.
- The tickets `remove-bootstrap-ingest`, `remove-plan-grammar` and `prompts-drop-plan` have merged, so the engine no longer builds itself from plan text.

Message: box-000050-42b264ae
