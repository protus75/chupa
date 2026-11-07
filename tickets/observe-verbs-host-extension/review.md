# Review: approve

The diff moves the watch and snapshot logic into chupa/observe.py with an explicit Context, adds lock-free read-only `watch` and `snapshot` verbs that read the configured state_dir, deletes watch.py and vscode-chupa/snapshot.py, runs every extension action through the `chupa.command` argv via Task or execFile, updates the required docs, and resolves all three prior review findings.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5b510ec62c1b79931b2ef51541d4bd662ff28b13",
  "stem": "observe-verbs-host-extension",
  "reviewed_sha": "5b510ec62c1b79931b2ef51541d4bd662ff28b13",
  "summary": "The diff moves the watch and snapshot logic into chupa/observe.py with an explicit Context, adds lock-free read-only `watch` and `snapshot` verbs that read the configured state_dir, deletes watch.py and vscode-chupa/snapshot.py, runs every extension action through the `chupa.command` argv via Task or execFile, updates the required docs, and resolves all three prior review findings.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
