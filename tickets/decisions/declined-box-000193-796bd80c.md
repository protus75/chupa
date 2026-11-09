---
id: declined-box-000193-796bd80c
kind: declined
link: box-000193-796bd80c
reopen_after_days: 60
---
A handoff review note says `shakeout-report-lane` and `verification-base-attribution` had no dependency edge, so either could land first. It also says no test checks that a missing named report still fails `verification` when the command that should produce it is excused as `base_red`.

Both tickets have merged, so the ordering half is moot. The rest asks only for a test. In current code a missing report is still a failure when its command is `base_red`: `VerificationGate.check` (`chupa/stages.py:1215-1225`) adds every `artifact.report_findings` entry without checking `base_red`, and `base_red` only drops the `exited <rc>` finding for that command. The note shows no runtime case where a missing report gets through.

- Both `shakeout-report-lane` and `verification-base-attribution` are in the merged list.
- `chupa/stages.py:1217`: `*artifact.report_findings` is added to the findings with no `base_red` check.
- `chupa/stages.py:1223`: the `not r.base_red` filter covers only the per-command exit-code findings.

Message: box-000193-796bd80c
