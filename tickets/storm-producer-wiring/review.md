# Review: approve

The diff meets every requirement of the 19.P3.storm-producer-wiring contract and stays inside the fence: Box gets an optional keyword-only arrival callback and occurrence_id, validated before any durable work and called once after the queue is read and before the dedup return or write; daemon gets a dormant storm_producer hook with no production caller; and the import-absence dormancy test is migrated to a calibrated behavioral proof.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1989c9fe5b492ad4d51efd3dcc76f67d5c76df95",
  "stem": "storm-producer-wiring",
  "reviewed_sha": "1989c9fe5b492ad4d51efd3dcc76f67d5c76df95",
  "summary": "The diff meets every requirement of the 19.P3.storm-producer-wiring contract and stays inside the fence: Box gets an optional keyword-only arrival callback and occurrence_id, validated before any durable work and called once after the queue is read and before the dedup return or write; daemon gets a dormant storm_producer hook with no production caller; and the import-absence dormancy test is migrated to a calibrated behavioral proof.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
