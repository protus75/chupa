---
id: declined-box-000280-e6a2823c
kind: declined
link: box-000280-e6a2823c
reopen_after_days: 30
---
During the notify-transport Implement run, an agent noted that the CLI `status` projection does not show the evidence behind a tree-mismatch escalation. It checked this on the base commit and left it out of its diff. The note does not say what an operator loses, which decision goes wrong, or which run was misread.

This is a display gap reported without a harmful result. The note names no incident where an operator, the drain, or the Reject queue acted wrongly because `status` lacked this evidence. Derived views like `status` are projections, and the evidence still exists in the journal and the ticket's run artifacts (`diagnosis.json`, `checks.json`, attempt spools). The request is also not bounded: it does not name the missing field, the escalation signal it would come from, or a measurable result after the change. No open or merged ticket covers it, so it is declined rather than tombstoned.

- The message class is `suggestion`, with origin `notify-transport` at stage `implement` and outcome `ok`. That stage passed, so the note is a side observation, not a failure report.
- The message has no `report`, `fixed_failure` or `proposed_spec_paths`, and it names no file, field or reproduction.
- Under the engine rules, files and the journal are the source of truth and `status` is only a projection of them. Leaving evidence out of the projection does not destroy it.
- No open ticket or decision record covers status output for tree-mismatch escalations.

Message: box-000280-e6a2823c
