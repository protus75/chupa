# Review: approve

The diff adds a required `coverage_map` keyword to `review_ticket`, computes out-of-fence coverage dependents before the first model call, snags mechanically with code `coverage_map` when a declared map is missing or invalid, adds the data block, Task rule and version bump to the spec, passes the map path from config in all four production callers, updates every test call site and the version pin, covers each case required by Scope in, and updates the docs row.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "6bb5d2dd990ad4e31ead2cfe5077492a14497915",
  "stem": "requisition-coverage-dependents",
  "reviewed_sha": "6bb5d2dd990ad4e31ead2cfe5077492a14497915",
  "summary": "The diff adds a required `coverage_map` keyword to `review_ticket`, computes out-of-fence coverage dependents before the first model call, snags mechanically with code `coverage_map` when a declared map is missing or invalid, adds the data block, Task rule and version bump to the spec, passes the map path from config in all four production callers, updates every test call site and the version pin, covers each case required by Scope in, and updates the docs row.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
