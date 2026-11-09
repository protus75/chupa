---
id: tombstone-box-000230-bd371ff4
kind: tombstone
link: declined-box-000079-2307b720
reopen_after_days: 90
---
The review-eval spike caught 18 of 18 planted defects and wrongly flagged none of 4 clean diffs. Each fixture plants one isolated, easy-to-find defect in a short diff, so the score is at its ceiling and cannot rank reviewers. The note asks the GO-grade set to add diffs with several defects, defects split across files, wrong tests that look correct, and clean diffs that look suspicious.

Registry record declined-box-000079-2307b720 already covers this request. It describes the same 18/18 and 0/4 ceiling and the same four kinds of harder fixtures. That record declined it because a missing eval fixture causes no wrong runtime behavior. This message adds no new evidence.

- declined-box-000079-2307b720 covers the same spike result (18/18 caught, 0/4 false snag) and asks for the same multi-defect, cross-file, plausible-but-wrong-test and suspicious-clean fixtures
- go-grade-machinery and go-grade-run are already merged; the message shows no wrong grading result from the current set
- The message reports no failure in a pipeline stage; it proposes more test coverage for the eval only

Message: box-000230-bd371ff4
