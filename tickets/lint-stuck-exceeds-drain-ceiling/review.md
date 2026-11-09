# Review: approve

The diff adds `stuck_ceiling_finding` to `chupa/__main__.py` and calls it from `_lint` with `drain.max_ticket_minutes`, so a ticket over the ceiling now fails lint with the drain's paved road; it also adds the unit test, integration test, and reproducer, and updates the docs row, with every changed file inside the fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a8eba92f848251b7f1b456cc2b29872a72638bb1",
  "stem": "lint-stuck-exceeds-drain-ceiling",
  "reviewed_sha": "a8eba92f848251b7f1b456cc2b29872a72638bb1",
  "summary": "The diff adds `stuck_ceiling_finding` to `chupa/__main__.py` and calls it from `_lint` with `drain.max_ticket_minutes`, so a ticket over the ceiling now fails lint with the drain's paved road; it also adds the unit test, integration test, and reproducer, and updates the docs row, with every changed file inside the fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
