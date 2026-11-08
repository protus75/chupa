# Review: snag

The selector parse, the shared excerpt function, the render and the docs are correct, and both prior findings are fixed. Two problems remain: acceptance criterion 3's test is in the wrong file, and the new unit tests leave out one required finding case.

## Findings

- [acceptance] tests/integration/test_requisition.py:283 Acceptance criterion 3 requires `tests/integration/test_tickets.py::test_context_whole_file_unchanged` to pass. The diff adds `test_context_whole_file_unchanged` to tests/integration/test_requisition.py instead, and test_tickets.py has no function by that name. Running the criterion's node ID reports 'not found', so the criterion is unmet. (do instead: Move `test_context_whole_file_unchanged` into tests/integration/test_tickets.py, using that file's `repo` fixture and `validate_ticket`, and render through `chupa.stages.implement_inputs`. Remove it from test_requisition.py, so the node ID named in criterion 3 exists and passes.)
- [acceptance] tests/unit/test_tickets_context.py:18 Scope-in requires the unit tests to cover each finding case, and that list includes 'a file listed both whole and by section'. `test_invalid_sections_raise` and `test_extension_checked_without_text` cover the wrong extension, a missing name or heading, and a duplicate heading, but no unit test covers mixing a whole file with its sections. That case is tested only in the disk-backed integration test. (do instead: Move the whole-versus-section conflict check into a pure function in chupa/tickets.py that takes the list of Context entries, and call it from parse_ticket. Add a unit test in tests/unit/test_tickets_context.py showing that `m.py` plus `m.py::B.run` yields the conflict and that two section entries of the same file do not.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1106dc0fb55e72c5d20e93c50854952821596ee7",
  "stem": "context-sections",
  "reviewed_sha": "1106dc0fb55e72c5d20e93c50854952821596ee7",
  "summary": "The selector parse, the shared excerpt function, the render and the docs are correct, and both prior findings are fixed. Two problems remain: acceptance criterion 3's test is in the wrong file, and the new unit tests leave out one required finding case.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/integration/test_requisition.py",
      "line": 283,
      "message": "Acceptance criterion 3 requires `tests/integration/test_tickets.py::test_context_whole_file_unchanged` to pass. The diff adds `test_context_whole_file_unchanged` to tests/integration/test_requisition.py instead, and test_tickets.py has no function by that name. Running the criterion's node ID reports 'not found', so the criterion is unmet.",
      "paved_road": "Move `test_context_whole_file_unchanged` into tests/integration/test_tickets.py, using that file's `repo` fixture and `validate_ticket`, and render through `chupa.stages.implement_inputs`. Remove it from test_requisition.py, so the node ID named in criterion 3 exists and passes.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/unit/test_tickets_context.py",
      "line": 18,
      "message": "Scope-in requires the unit tests to cover each finding case, and that list includes 'a file listed both whole and by section'. `test_invalid_sections_raise` and `test_extension_checked_without_text` cover the wrong extension, a missing name or heading, and a duplicate heading, but no unit test covers mixing a whole file with its sections. That case is tested only in the disk-backed integration test.",
      "paved_road": "Move the whole-versus-section conflict check into a pure function in chupa/tickets.py that takes the list of Context entries, and call it from parse_ticket. Add a unit test in tests/unit/test_tickets_context.py showing that `m.py` plus `m.py::B.run` yields the conflict and that two section entries of the same file do not.",
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
