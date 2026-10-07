# Review: approve

The diff adds the missing in-memory carrier and its construction order to the 19.P3.admission-holds-activation entry. That carrier is the required keyword-only `Checkout.control_inbox`, which is built before `pipeline(checkout)` and forwarded through `bind` and `build_control`. The diff also fences and migrates the direct `drain`, `bind` and `Checkout` callers in `tests/test_drain.py`, with a named test. Every stated fact matches the merged code (`runner.Checkout` has no carrier, `PauseConsumer` builds its own `control_inbox`, and `drain.drain` calls `build_control` after taking the lock), and no edit falls outside the unit.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4ca7ffa722a44d645994e50c90a910486100ff3b",
  "stem": "harden-admission-holds-activation-3",
  "reviewed_sha": "4ca7ffa722a44d645994e50c90a910486100ff3b",
  "summary": "The diff adds the missing in-memory carrier and its construction order to the 19.P3.admission-holds-activation entry. That carrier is the required keyword-only `Checkout.control_inbox`, which is built before `pipeline(checkout)` and forwarded through `bind` and `build_control`. The diff also fences and migrates the direct `drain`, `bind` and `Checkout` callers in `tests/test_drain.py`, with a named test. Every stated fact matches the merged code (`runner.Checkout` has no carrier, `PauseConsumer` builds its own `control_inbox`, and `drain.drain` calls `build_control` after taking the lock), and no edit falls outside the unit.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
