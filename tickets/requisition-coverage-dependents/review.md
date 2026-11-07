# Review: approve

The diff adds a required keyword `coverage_map` to `review_ticket`, with no default. Before any model call it computes the out-of-fence coverage dependents, or snags with code `coverage_map` when a declared map is missing or invalid. The dependents go to the spec as a `coverage_dependents` block with the fenced-or-cleared Task rule, the spec version moves to 3.1, every caller and test is updated, and the doc row is updated.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3728cbfddc67bd633c37922bcf2e5cb310c9d838",
  "stem": "requisition-coverage-dependents",
  "reviewed_sha": "3728cbfddc67bd633c37922bcf2e5cb310c9d838",
  "summary": "The diff adds a required keyword `coverage_map` to `review_ticket`, with no default. Before any model call it computes the out-of-fence coverage dependents, or snags with code `coverage_map` when a declared map is missing or invalid. The dependents go to the spec as a `coverage_dependents` block with the fenced-or-cleared Task rule, the spec version moves to 3.1, every caller and test is updated, and the doc row is updated.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
