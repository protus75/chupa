---
id: tombstone-box-000264-40488fda
kind: tombstone
link: declined-box-000168-4260979f
reopen_after_days: 90
---
This note says the `diagnosis-eval-run` ticket's 120m stuck budget is exactly its worst case of 12 calls at the 600s `CALL_STUCK_S` limit. A stuck kill would end the run as `timeout`, and harvest would then wipe the worktree that holds the partial report, so a re-offer would start from zero. It proposes either a larger stuck budget or keeping the report outside the worktree. Registry record 000168 already declined this same request.

The request matches declined record 000168 in substance: the same ticket, the same 12 x 600s = 120m stuck budget, the same chain where a timeout leads harvest to wipe the worktree and lose the report, and the same two proposed fixes. `diagnosis-eval-run` has since merged, so the risk this note describes no longer applies to any ticket still waiting to run.

- Registry record declined-box-000168-4260979f describes the same 120m stuck budget against 12 x CALL_STUCK_S, the same harvest wipe of the partial report, and the same two fixes.
- diagnosis-eval-run is in the merged stems list.
- time-budget-stuck-exceeds-expected is merged.

Message: box-000264-40488fda
