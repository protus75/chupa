---
id: tombstone-box-000408-fdc36464
kind: tombstone
link: declined-box-000399-63c8360a
reopen_after_days: 30
---
On commit-lock attempt 6, Implement returned premise_failed after a short run of read-only steps. Its only finding admitted the work was unfinished and named no contradiction or missing scope. The engine accepts any premise_failed, and with premise_bounce at 1 the ticket went straight to the Reject queue. The note proposes either that the implement spec say unfinished or large work is never premise_failed, or that Check refuse a premise_failed whose findings cite no contradiction, criterion or forced path and treat it as a retryable failure.

This repeats the gap already decided in registry record declined-box-000399-63c8360a. That record covers the same incident (commit-lock Implement attempt 6 returning premise_failed after a short partial run with no contradiction or missing scope), the same harm (a spent premise_bounce cap sending a buildable ticket to the Reject queue), and the same repair (implement.md requires each premise_failed finding to cite a specific defect and says unfinished or large work is not a premise failure). The alternative repair here, a Check-side refusal of uncited premise_failed findings, fixes the same gap at a different place. It is not a separate behavior gap. Reopen if a premise_failed with no cited contradiction, criterion or forced path sends a ticket to the Reject queue in a run other than commit-lock attempts 6 and 8.

- Message: commit-lock attempt 6, codex Implement returned premise_failed after 118s and 9 read-only steps, finding 'no contradiction or missing scope has been established'.
- Registry declined-box-000399-63c8360a: retro/40 found commit-lock Implement attempts 6 and 8 returned premise_failed after short partial runs, each admitting no contradiction or missing scope; proposed implement.md require a cited defect and state unfinished work is not premise_failed.
- commit-lock is now in the merged set, so the incident ticket itself is no longer blocked.

Message: box-000408-fdc36464
