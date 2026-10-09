# Review: approve

When the line consumer raises, ProcessExec.run now stops calling it but keeps reading both pipes to EOF and waits for the child, then re-raises the consumer's first exception with the full stdout and stderr attached; CliAdapter writes the scrubbed events.jsonl and stderr.txt before the exception propagates, and timeout and cancellation still kill the process group, keep their own exception type, and record the consumer failure as the cause.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "bea4e380b8002bd6f31c6cd362feb42d83a5d7ac",
  "stem": "consumer-error-keeps-capture",
  "reviewed_sha": "bea4e380b8002bd6f31c6cd362feb42d83a5d7ac",
  "summary": "When the line consumer raises, ProcessExec.run now stops calling it but keeps reading both pipes to EOF and waits for the child, then re-raises the consumer's first exception with the full stdout and stderr attached; CliAdapter writes the scrubbed events.jsonl and stderr.txt before the exception propagates, and timeout and cancellation still kill the process group, keep their own exception type, and record the consumer failure as the cause.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
