# Review: approve

The diff calls intake at the top of each `_Drain.run` iteration, after the stop check and before the retro check and `_scan`, and inside the lock's try/finally, so an `IntakeRefused` ends the drain the same way the startup intake's refusal does and the lock is still released. It adds or rewrites all four tests the ticket asks for and updates section 7.1 of `docs/how-chupa-works.md`.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "749227c3aa15e24770731444dbcfd88a63ffbcf0",
  "stem": "drain-intake-each-loop",
  "reviewed_sha": "749227c3aa15e24770731444dbcfd88a63ffbcf0",
  "summary": "The diff calls intake at the top of each `_Drain.run` iteration, after the stop check and before the retro check and `_scan`, and inside the lock's try/finally, so an `IntakeRefused` ends the drain the same way the startup intake's refusal does and the lock is still released. It adds or rewrites all four tests the ticket asks for and updates section 7.1 of `docs/how-chupa-works.md`.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
