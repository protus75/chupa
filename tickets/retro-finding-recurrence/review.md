# Review: approve

The diff adds `prior_findings` to the retro prompt and rejects unknown `recurs` ids as retry findings. Recurrences are counted on the existing message, idempotent per occurrence id and safe across a crash, and tombstones still go through the re-report path. Only a ticket fix that has merged causes a reopen, after which Author can file a new ticket. All four prior-review gaps now have unit or integration tests.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e68b24faaf61dbf5518b8812d9101eecaeffb21e",
  "stem": "retro-finding-recurrence",
  "reviewed_sha": "e68b24faaf61dbf5518b8812d9101eecaeffb21e",
  "summary": "The diff adds `prior_findings` to the retro prompt and rejects unknown `recurs` ids as retry findings. Recurrences are counted on the existing message, idempotent per occurrence id and safe across a crash, and tombstones still go through the re-report path. Only a ticket fix that has merged causes a reopen, after which Author can file a new ticket. All four prior-review gaps now have unit or integration tests.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
