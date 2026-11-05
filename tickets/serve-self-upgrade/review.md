# Review: snag

Serve's self-upgrade handoff is mostly correct, but its idle check also waits on policy-held merge candidates, so a held merge can stop admission indefinitely without ever handing off.

## Findings

- [logic] chupa/serve.py:311 `upgrade_idle` requires `not self.queue.held`. `MergeQueue.held` holds candidates parked on a review-policy hold, which only a human release or later coverage clears (mergequeue.py:145-150). Once an engine change is seen, `admissible` and `dispatch` stop admitting new work. If a candidate is held at that point, serve stays in that state until someone releases the hold: it admits nothing and never hands off. That is a fail-stuck state. The ticket's idle condition is only 'no ticket is running and the merge queue has no pending or active candidate'. Held admissions already survive a restart through the journal (`held_admissions`), so a handoff does not need to wait for them. (do instead: Drop the `self.queue.held` term so idle means: no running ticket, and the queue has no pending or active candidate. Add a test where one candidate is held when the engine tree changes, and assert that serve still hands off.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5cedbdac3a43c8df8116203ef39f8f42b4401490",
  "stem": "serve-self-upgrade",
  "reviewed_sha": "5cedbdac3a43c8df8116203ef39f8f42b4401490",
  "summary": "Serve's self-upgrade handoff is mostly correct, but its idle check also waits on policy-held merge candidates, so a held merge can stop admission indefinitely without ever handing off.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 311,
      "message": "`upgrade_idle` requires `not self.queue.held`. `MergeQueue.held` holds candidates parked on a review-policy hold, which only a human release or later coverage clears (mergequeue.py:145-150). Once an engine change is seen, `admissible` and `dispatch` stop admitting new work. If a candidate is held at that point, serve stays in that state until someone releases the hold: it admits nothing and never hands off. That is a fail-stuck state. The ticket's idle condition is only 'no ticket is running and the merge queue has no pending or active candidate'. Held admissions already survive a restart through the journal (`held_admissions`), so a handoff does not need to wait for them.",
      "paved_road": "Drop the `self.queue.held` term so idle means: no running ticket, and the queue has no pending or active candidate. Add a test where one candidate is held when the engine tree changes, and assert that serve still hands off.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
