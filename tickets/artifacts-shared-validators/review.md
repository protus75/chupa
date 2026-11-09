# Review: approve

The diff moves the three repeated validator bodies into private module-level checkers in chupa/artifacts.py, calls them from all nine validators with byte-identical messages, leaves ShakeoutEntry and HostLoopReport._ordered untouched, and adds the three named in-memory unit tests, which would fail on any regression the ticket names.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5a31817bc6f6b3df27e0005f58e0cf150755af25",
  "stem": "artifacts-shared-validators",
  "reviewed_sha": "5a31817bc6f6b3df27e0005f58e0cf150755af25",
  "summary": "The diff moves the three repeated validator bodies into private module-level checkers in chupa/artifacts.py, calls them from all nine validators with byte-identical messages, leaves ShakeoutEntry and HostLoopReport._ordered untouched, and adds the three named in-memory unit tests, which would fail on any regression the ticket names.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
