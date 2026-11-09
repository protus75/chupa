---
id: tombstone-box-000229-457522ce
kind: tombstone
link: declined-box-000078-4774e46d
reopen_after_days: 90
---
The review eval runs each fixture through the shared Driver, which uses `caps.retry` (6) as its limit on schema re-prompts. A reviewer that keeps returning invalid JSON can therefore spend up to 7 opus calls on one fixture. The note proposes a lower cap just for the eval once a flat per-run USD cap exists.

Registry record declined-box-000078-4774e46d already decided this same suggestion: the eval Driver takes `caps.retry` as its per-fixture re-prompt cap, the worst case is retry+1 (7) opus calls, and an eval-local cap is proposed once the Phase 6 per-run USD cap lands. The new message adds no new evidence of harm.

- Message: eval Driver uses caps.retry (6) as its per-fixture schema re-prompt cap, so the worst case is 7 opus calls; it asks for an eval-local cap when the per-run USD cap lands.
- declined-box-000078-4774e46d: same Driver/caps.retry observation, same worst case of 7 calls, same eval-local cap proposal tied to a flat per-run USD cap.

Message: box-000229-457522ce
