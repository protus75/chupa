# Review: snag

The new `drive` refusal stops `serve` and strands the stem in `running` when a stem at its attempts total was never routed; separately and not blocking, `eval/shakeout/drain.py` (outside the fence) appears to go red by reading under `premise_bounce: 1` while `tests/test_shakeout.py` overrides that cap, so it should be filed.

## Findings

- [logic] chupa/runner.py:150 `Scheduler.dispatch_next` holds only stems in `reject_queue` and never checks caps, and `_settle`'s routing of spent stems exists only in drain. A stem at its attempts total with no routed terminal therefore still reaches `serve`'s dispatch. This happens when the journal already holds at least `caps.attempts` failures from before this change, or when an operator lowers `caps.attempts`. `serve.py:120` journals `running`, then this guard raises `Refusal`. Nothing between `drive` and `guarded()` catches it, so `serve` exits with code 2, the stem stays `running` with no terminal, and it never routes to the Reject queue. Once reconcile reaps the stem as `abandoned`, it is not in `reject_queue`, so the next `serve` can dispatch it and fail the same way. The ticket requires a stem at its total to route to the Reject queue with reason "attempts cap spent". No test covers this guard on the `serve` path. (do instead: Replace the raise in `drive` with a single routed terminal that does not count as a failed attempt, for example `{"to": "abandoned", "reason": spent_reason("attempts"), "dispatch": "reject_queue", "routed": "reject_queue"}`, and return its state. `_admit` can keep refusing for `chupa run`, which refuses before journaling `running`. Add a test that drives an unrouted stem at its total through the daemon dispatch path and asserts it lands in the Reject queue, makes no model call, and does not stop the worker.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "c2d56ad43ac876135ca8579bf237f307ecf58e6e",
  "stem": "attempts-cap",
  "reviewed_sha": "c2d56ad43ac876135ca8579bf237f307ecf58e6e",
  "summary": "The new `drive` refusal stops `serve` and strands the stem in `running` when a stem at its attempts total was never routed; separately and not blocking, `eval/shakeout/drain.py` (outside the fence) appears to go red by reading under `premise_bounce: 1` while `tests/test_shakeout.py` overrides that cap, so it should be filed.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/runner.py",
      "line": 150,
      "message": "`Scheduler.dispatch_next` holds only stems in `reject_queue` and never checks caps, and `_settle`'s routing of spent stems exists only in drain. A stem at its attempts total with no routed terminal therefore still reaches `serve`'s dispatch. This happens when the journal already holds at least `caps.attempts` failures from before this change, or when an operator lowers `caps.attempts`. `serve.py:120` journals `running`, then this guard raises `Refusal`. Nothing between `drive` and `guarded()` catches it, so `serve` exits with code 2, the stem stays `running` with no terminal, and it never routes to the Reject queue. Once reconcile reaps the stem as `abandoned`, it is not in `reject_queue`, so the next `serve` can dispatch it and fail the same way. The ticket requires a stem at its total to route to the Reject queue with reason \"attempts cap spent\". No test covers this guard on the `serve` path.",
      "paved_road": "Replace the raise in `drive` with a single routed terminal that does not count as a failed attempt, for example `{\"to\": \"abandoned\", \"reason\": spent_reason(\"attempts\"), \"dispatch\": \"reject_queue\", \"routed\": \"reject_queue\"}`, and return its state. `_admit` can keep refusing for `chupa run`, which refuses before journaling `running`. Add a test that drives an unrouted stem at its total through the daemon dispatch path and asserts it lands in the Reject queue, makes no model call, and does not stop the worker.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
