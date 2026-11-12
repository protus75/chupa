# Review: snag

The shared apply function, the single `inbox.known` assignment in `build_control`, the in-flight monitor settle, the tests, the regression script and the docs all match the ticket, but the between-ticket checkpoint only settles after `consumer.checkpoint()` returns, so a confirm or reject accepted while the drain is paused stays unapplied until resume, which `serve` does not do.

## Findings

- [logic] chupa/drain.py:262 `await settle_admissions(checkout)` runs only after `asyncio.wait((pending, watcher))` returns. While a pause is held, `pending` is `PauseConsumer.checkpoint()` (chupa/daemon.py:229). That loop keeps calling `poll()` -> `inbox.consume()`, which journals the confirm or reject as `control_decision` `accepted`, and it does not return until resume or kill. So on a paused drain, an accepted admission leaves the draft at `state: draft` for as long as the pause lasts. The scope says to settle 'wherever the drain consumes its inbox ... in the between-ticket control checkpoint', and the goal says the operator sees the verdict within seconds. `serve` settles in its merge poll whether or not it is paused, so the two engines now apply the same request with different timing. (do instead: Inside `control_checkpoint` in chupa/drain.py, keep settling while `pending` is still running. For example, run a small task that does `while not pending.done(): await settle_admissions(checkout); await consumer.sleep(0.1)`, add it to the awaited and cancelled set next to `watcher`, and keep the final settle after the wait. Optionally add a paused-drain case to tests/integration/test_drain_admissions.py.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "996b14b8e462907c422728bbf13109be3bdd73e2",
  "stem": "drain-settles-admissions",
  "reviewed_sha": "996b14b8e462907c422728bbf13109be3bdd73e2",
  "summary": "The shared apply function, the single `inbox.known` assignment in `build_control`, the in-flight monitor settle, the tests, the regression script and the docs all match the ticket, but the between-ticket checkpoint only settles after `consumer.checkpoint()` returns, so a confirm or reject accepted while the drain is paused stays unapplied until resume, which `serve` does not do.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/drain.py",
      "line": 262,
      "message": "`await settle_admissions(checkout)` runs only after `asyncio.wait((pending, watcher))` returns. While a pause is held, `pending` is `PauseConsumer.checkpoint()` (chupa/daemon.py:229). That loop keeps calling `poll()` -> `inbox.consume()`, which journals the confirm or reject as `control_decision` `accepted`, and it does not return until resume or kill. So on a paused drain, an accepted admission leaves the draft at `state: draft` for as long as the pause lasts. The scope says to settle 'wherever the drain consumes its inbox ... in the between-ticket control checkpoint', and the goal says the operator sees the verdict within seconds. `serve` settles in its merge poll whether or not it is paused, so the two engines now apply the same request with different timing.",
      "paved_road": "Inside `control_checkpoint` in chupa/drain.py, keep settling while `pending` is still running. For example, run a small task that does `while not pending.done(): await settle_admissions(checkout); await consumer.sleep(0.1)`, add it to the awaited and cancelled set next to `watcher`, and keep the final settle after the wait. Optionally add a paused-drain case to tests/integration/test_drain_admissions.py.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
