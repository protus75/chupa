# Review: approve

The plugin guards exactly the listed calls during setup, call and teardown only, and restores them afterwards. It reads the budget through parse_gate (60 seconds when test-gate.toml is absent) and enforces it on the xdist controller. The tests now check the setup and teardown errors one test at a time, which closes the prior finding, and the section 12 doc bullet is added.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "063ca47f5a979c8b16e79c1c10463a92603df83f",
  "stem": "testguard",
  "reviewed_sha": "063ca47f5a979c8b16e79c1c10463a92603df83f",
  "summary": "The plugin guards exactly the listed calls during setup, call and teardown only, and restores them afterwards. It reads the budget through parse_gate (60 seconds when test-gate.toml is absent) and enforces it on the xdist controller. The tests now check the setup and teardown errors one test at a time, which closes the prior finding, and the section 12 doc bullet is added.",
  "findings": [],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
