---
id: declined-box-000074-a6497ff4
kind: declined
link: box-000074-a6497ff4
reopen_after_days: 90
---
The eval harness `author` command picks the model that authors fixture cases from a command argument (codex at high effort by default) and calls that adapter directly instead of going through config routing. No routing surface covers fixture authoring. The note asks the plan to state how the fixture author is chosen, so that regenerating from the plan gives the same result.

The request only changes plan wording. `CHUPA_PLAN.md` is a frozen bootstrap record that is never edited, and fixture authoring is an operator-run eval tool, not an engine stage. The note reports no wrong runtime behavior: choosing the author with an explicit argument works and can be reproduced from the command line. Wanting a routing row for it is a preference, not a measured harm.

- The message asks for changes to plan text (19.P1/19.P6) and names no runtime failure.
- Project conduct says CHUPA_PLAN.md is frozen and never edited.
- Earlier plan-reconciliation notes were declined on the same grounds (declined-box-000050-42b264ae, declined-box-000073-375ea556).

Message: box-000074-a6497ff4
