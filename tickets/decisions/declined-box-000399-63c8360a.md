---
id: declined-box-000399-63c8360a
kind: declined
link: box-000399-63c8360a
reopen_after_days: 30
---
Retro/40 found that commit-lock Implement attempts 6 and 8 returned premise_failed after short partial runs. Each finding admitted it had found no contradiction and no missing scope, only unfinished work. The two bounces spent the premise_bounce cap and sent a buildable ticket to the Reject queue. The finding asks implement.md to require each premise_failed finding to cite a specific defect and to say that large or unfinished work is not a premise failure.

The finding's premise is that implement.md never says unfinished or large work is not a premise failure. Current main does say it. chupa/specs/implement.md line 78 reads: "Running out of time, or a change that is only large, is never `premise_failed`." Lines 76-78 limit premise_failed to three cases: the bug does not reproduce, the criteria contradict existing behavior or each other, or the criteria force an edit outside the fence. Lines 121-123 require every finding to be coded `premise` and to name the path it concerns. The proposed spec edit is therefore already in place, so a new ticket would duplicate existing text. The incident ticket commit-lock has also merged since. Reopen within the window if an Implement reply under the current spec returns premise_failed and its finding cites only unfinished or large work. That would show the prose rule is not enough, and the repair would then be a mechanical check on the reply, not more spec wording.

- chupa/specs/implement.md:76-78 limits premise_failed to non-reproduction, contradiction, or a forced edit outside the fence, and states "Running out of time, or a change that is only large, is never `premise_failed`."
- chupa/specs/implement.md:121-123 requires every premise_failed finding to be coded `premise` and to name the contradicted file, the file outside the fence, or the malformed ticket.
- commit-lock is in the merged set, so the stranded ticket from the incident has since landed.
- Related open ticket diagnose-spec-reachable-road-rule covers a different cause: a Diagnose clause that invited a premise bounce.

Message: box-000399-63c8360a
