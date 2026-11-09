---
id: declined-box-000180-67ad77f0
kind: declined
link: box-000180-67ad77f0
reopen_after_days: 90
---
A bootstrap handoff note measured the `reject-queue-verbs` Implement prompt at about 113k characters, against a 120k limit at the top of the escalation ladder. It asked for a new measurement after earlier batches grew `chupa/runner.py`, and for `tests/test_drain_upgrade.py` to move to On-demand context if the prompt got close to the limit.

The ticket has already merged (`reject-queue-verbs` is in the merged list), so its Implement render can no longer go over the bound and there is nothing left to measure. The note was a precaution, and it never reported an over-bound refusal. A render that is over the bound already parks as `premise_failed` with a `render_over_bound` finding, so it cannot fail silently. The earlier spine-diagnosis render-headroom note (declined-box-000171-59198372) was declined for the same reason.

- `reject-queue-verbs` is listed among the merged stems.
- The message is a precautionary measurement of the prompt size, not a reported over-bound failure.
- declined-box-000171-59198372 declined the same kind of render-headroom note for spine-diagnosis.
- declined-box-000101-8a149c25: over-bound renders already park as `premise_failed` with a `render_over_bound` finding and go to their own paved road.

Message: box-000180-67ad77f0
