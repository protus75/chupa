# Review: approve

The diff wraps the `parse_ticket` call in `_dead_dependents` in `try`/`except TicketInvalid: continue`, using the `TicketInvalid` import that already exists. It adds the integration test, the unit test, and the carried reproducer, all as the ticket specifies and all inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0f48e44bf71d8888dfdce27812cb2051534f8925",
  "stem": "reject-survives-invalid-ticket",
  "reviewed_sha": "0f48e44bf71d8888dfdce27812cb2051534f8925",
  "summary": "The diff wraps the `parse_ticket` call in `_dead_dependents` in `try`/`except TicketInvalid: continue`, using the `TicketInvalid` import that already exists. It adds the integration test, the unit test, and the carried reproducer, all as the ticket specifies and all inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
