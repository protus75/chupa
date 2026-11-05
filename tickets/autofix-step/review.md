# Review: approve

The autofix step matches the ticket: it uses the right file list, snapshots bytes and commits only tool-changed files as chupa(<stem>): autofix, and on failure it stops, restores the files, treats the failure as hard and blocks seed review; config, tests and docs match.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3588d358ebef3d29476c565948922f5de52aa3c0",
  "stem": "autofix-step",
  "reviewed_sha": "3588d358ebef3d29476c565948922f5de52aa3c0",
  "summary": "The autofix step matches the ticket: it uses the right file list, snapshots bytes and commits only tool-changed files as chupa(<stem>): autofix, and on failure it stops, restores the files, treats the failure as hard and blocks seed review; config, tests and docs match.",
  "findings": [],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
