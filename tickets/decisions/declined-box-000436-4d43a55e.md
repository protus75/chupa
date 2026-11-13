---
id: declined-box-000436-4d43a55e
kind: declined
link: box-000436-4d43a55e
reopen_after_days: 30
---
This suggestion was carried over from the fungo host on 2026-11-13. It asks the host authoring guide to require more detail in the Goal of a `kind: bug` ticket. The Goal would state the wrong output that was seen and the command that produced it. It would state the expected output and the spec that sets it. It would name the suspected cause and at least one other location the agent must check and rule out. When an earlier ticket tried to fix the same bug, it would list the fix shapes the agent must not ship. The note says it overlaps the CORE_TEMPLATE Diagnosis rules and cites no incident.

This is a preference about how to write guidance. It shows no current harmful behavior. The note itself says it cites no incident. It names no run, ticket or retro where a bug ticket's Goal led an agent to ship a fix built on a wrong diagnosis. Without that, nothing measurable would change after the edit. It also overlaps rules that already exist. The CORE_TEMPLATE Diagnosis section already requires naming the root cause before any edit, and the merged `new-bug-evidence-upfront`, `bug-gate-grammar` and `bug-evidence-intake` tickets already require a `kind: bug` ticket to carry a reproducer of the wrong behavior. The earlier fungo authoring-guide suggestions from the same day (records 000431, 000432, 000433 and 000435) were declined for the same reason. Reopen if a chupa or host run shows a bug ticket shipping a fix that passed on a misdiagnosed premise because its Goal left out the expected output, the spec, or the other locations to rule out.

- Message summary says 'No incident cited.'
- CORE_TEMPLATE Diagnosis rules already require naming the root cause against the canonical spec before editing (CLAUDE.md managed block, Diagnosis section).
- Merged tickets new-bug-evidence-upfront, bug-gate-grammar and bug-evidence-intake already require a reproducer of the wrong behavior on bug tickets.
- The other fungo authoring-guide suggestions from 2026-11-13 were declined for having no incident: declined-box-000431-caf1a286, declined-box-000432-6db34da4, declined-box-000433-cc573d5a, declined-box-000435-b106dd5f.

Message: box-000436-4d43a55e
