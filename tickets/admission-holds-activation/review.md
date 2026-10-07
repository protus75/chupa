# Review: approve

The diff passes one shared `build_control` consumer from the `run`/`drain` and daemon-core roots through `Checkout.control` into `compose_pipeline` and `drain`, and both refuse a missing consumer. Red-streak and tree-mismatch holds are journaled with a fresh `uuid4` identity before the queue is marked held, `hold` is called and escalation runs, in that order. A hold is released only at `process()`'s serial boundary, and only once the consumer's durable accepted decision has added it to `released_hold_ids`. Discovery is published through the explicit `write_active(hold_id=...)` selector, preferring the dispatch pause, and every named test and caller migration stays inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "d69556da05993d15cf89786fa45184aa78f808ba",
  "stem": "admission-holds-activation",
  "reviewed_sha": "d69556da05993d15cf89786fa45184aa78f808ba",
  "summary": "The diff passes one shared `build_control` consumer from the `run`/`drain` and daemon-core roots through `Checkout.control` into `compose_pipeline` and `drain`, and both refuse a missing consumer. Red-streak and tree-mismatch holds are journaled with a fresh `uuid4` identity before the queue is marked held, `hold` is called and escalation runs, in that order. A hold is released only at `process()`'s serial boundary, and only once the consumer's durable accepted decision has added it to `released_hold_ids`. Discovery is published through the explicit `write_active(hold_id=...)` selector, preferring the dispatch pause, and every named test and caller migration stays inside the scope fence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
