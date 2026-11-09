---
id: tombstone-box-000215-e2f984b2
kind: tombstone
link: declined-box-000050-42b264ae
reopen_after_days: 90
---
The frozen plan's section 8 mentions only the quoted `[chupa-data:` form. It never gives the raw data-block delimiter or the grammar of the begin/end lines that `chupa/specs.py` builds from parts as `DATA_DELIM`. The note asks the plan to describe that grammar so a regeneration from the plan would produce the same delimiter.

This is the same request already settled in registry record declined-box-000050-42b264ae: change the plan text to state the data-block delimiter and begin/end line grammar. The plan is also frozen, and the note reports no runtime failure.

- Registry record declined-box-000050-42b264ae records the same gap: section 8 names only `[chupa-data:`, and the delimiter grammar built as `DATA_DELIM` in `chupa/specs.py` is not stated.
- CHUPA_PLAN.md is a frozen bootstrap design record and is never edited (CLAUDE.md section A).
- The message describes a mismatch in plan wording, not wrong runtime behavior.

Message: box-000215-e2f984b2
