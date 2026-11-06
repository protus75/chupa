# Review: approve

The diff checks for a due retro only between tickets: before the first dispatch, or once the last dispatched stem has settled, is in the Reject queue, or is held (drought, storm or premise park). Its new test pins both orderings, and section 9.5 of the docs now says the retro runs between tickets.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "d9bf9ed7a33485d3edf9140627aa40abfb6d4138",
  "stem": "retro-between-tickets",
  "reviewed_sha": "d9bf9ed7a33485d3edf9140627aa40abfb6d4138",
  "summary": "The diff checks for a due retro only between tickets: before the first dispatch, or once the last dispatched stem has settled, is in the Reject queue, or is held (drought, storm or premise park). Its new test pins both orderings, and section 9.5 of the docs now says the retro runs between tickets.",
  "findings": [],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
