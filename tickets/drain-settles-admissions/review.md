# Review: approve

The diff meets every acceptance criterion and fixes the prior review's paused-drain finding: `build_control` alone now sets `inbox.known`, admission logic moves into one shared `runner.apply_admission` used by both serve and drain, the drain settles verdicts while a ticket is in flight and on every pause-loop sleep through `settling_sleep` (covered by `test_confirm_during_pause`), refusals log `verdict_refused`, and the docs, tests and regression script match the ticket.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "213d64c1ad062d9046c0a7c9a711bc107756e6e1",
  "stem": "drain-settles-admissions",
  "reviewed_sha": "213d64c1ad062d9046c0a7c9a711bc107756e6e1",
  "summary": "The diff meets every acceptance criterion and fixes the prior review's paused-drain finding: `build_control` alone now sets `inbox.known`, admission logic moves into one shared `runner.apply_admission` used by both serve and drain, the drain settles verdicts while a ticket is in flight and on every pause-loop sleep through `settling_sleep` (covered by `test_confirm_during_pause`), refusals log `verdict_refused`, and the docs, tests and regression script match the ticket.",
  "findings": [],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
