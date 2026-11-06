# Review: snag

The diff removes the plan grammar, resolver, fence anchors and watchdog anchors as the ticket asks, but it also deletes a spec-lint test that has nothing to do with the plan.

## Findings

- [scope] tests/test_specs.py:280 The deleted `--- Plan contract resolver ---` block also removed `test_lint_reports_file_line_numbers`. That test checks that `lint_spec` reports the correct file line for a `data_outside_block` finding. `lint_spec` is not one of the deleted functions, and nothing else in tests/test_specs.py checks `finding.line`, so the change silently drops coverage of behaviour the ticket keeps. The Definition of rejected forbids changes to anything outside the plan machinery. (do instead: Restore `test_lint_reports_file_line_numbers` unchanged in tests/test_specs.py, for example right after `test_validate_data_blocks_flags_unpaired_delimiter`. Delete only the tests that call the removed plan functions.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "acc8431b05500401249800a8ad7a70cb3f62ab22",
  "stem": "remove-plan-grammar",
  "reviewed_sha": "acc8431b05500401249800a8ad7a70cb3f62ab22",
  "summary": "The diff removes the plan grammar, resolver, fence anchors and watchdog anchors as the ticket asks, but it also deletes a spec-lint test that has nothing to do with the plan.",
  "findings": [
    {
      "code": "scope",
      "path": "tests/test_specs.py",
      "line": 280,
      "message": "The deleted `--- Plan contract resolver ---` block also removed `test_lint_reports_file_line_numbers`. That test checks that `lint_spec` reports the correct file line for a `data_outside_block` finding. `lint_spec` is not one of the deleted functions, and nothing else in tests/test_specs.py checks `finding.line`, so the change silently drops coverage of behaviour the ticket keeps. The Definition of rejected forbids changes to anything outside the plan machinery.",
      "paved_road": "Restore `test_lint_reports_file_line_numbers` unchanged in tests/test_specs.py, for example right after `test_validate_data_blocks_flags_unpaired_delimiter`. Delete only the tests that call the removed plan functions.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
