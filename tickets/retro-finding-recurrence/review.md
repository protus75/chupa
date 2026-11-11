# Review: snag

The production code for recurrence counting, the merged-fix reopen and Author recovery is correct, but several acceptance criteria are untested or are tested in a different file from the one the ticket names.

## Findings

- [acceptance] tests/integration/test_retro.py:520 Criterion 2 requires tests/unit/test_retro_recurrence.py to show that a retro reply whose `recurs` names an id not in prior_findings is rejected with a retry finding. That test was written only in the integration file tests/integration/test_retro.py, and tests/unit/test_retro_recurrence.py has no such test. (do instead: Add a disk-free test to tests/unit/test_retro_recurrence.py. It should exercise the `recurs` validation (the `validate_recurrences` review hook or the retro stage with fakes) and assert that an unknown `recurs` id produces a `retro_recurs` fail finding and files nothing.)
- [acceptance] tests/unit/test_retro_recurrence.py:68 Criterion 3 asks for three unit cases through `Retro.emit_proposals`: (a) a named pending message has `recurrences` 1, not 2, after a second identical call; (b) a message resolved as a merged ticket is reopened as `pending`, with `reopen` true and no resolution; (c) a running-ticket case. `test_emit_counts_each_running_fix_once` covers only (c). Neither the pending case nor the merged-reopen case goes through `emit_proposals` in the unit test. (do instead: Extend the emit_proposals unit test, for example by parametrizing it, with a pending message called twice for the same report (assert `recurrences == 1` and zero `enqueue` calls) and a message resolved as a ticket whose journal state is `merged` (assert `pending`, `reopen` true, `resolution` None).)
- [acceptance] tests/unit/test_retro_recurrence.py:51 Criterion 4's first bullet requires a direct call on `Box.record_recurrence` showing that the count rises once per occurrence id, with a repeat of the same id as a no-op. `test_receipt_recovers_both_sides_of_write` uses only one pre-seeded occurrence. No direct call shows the count rising for two distinct occurrence ids, or a fresh call (no seeded intent) with `reopen=True` writing back the merged ticket's message. (do instead: Add a direct `Box.record_recurrence` test with a fake FileSystem and MemoryJournal. Call it with occurrence ids 'a', 'a' and 'b' and assert counts 1, 1 and 2. Add a fresh `reopen=True` call on a message resolved as a ticket and assert it is written back `pending`, with `reopen` true and `resolution`/`verdict` None.)
- [acceptance] tests/integration/test_retro_box.py:212 Criterion 7's tombstone bullet requires that `reports` rises through the re-report path and that the third report reopens the tombstone as it does today. The parametrized test checks only `reports == 1` after one recurrence and never drives a third report to show the reopen. (do instead: Add a tombstone case that emits recurrence proposals from three distinct retro reports, or seeds `reports=2` first. Assert that the third leaves the message `pending`, with `reopen` true and no resolution.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "32a4bccd837c71f58b72263e641529ffef77b6f8",
  "stem": "retro-finding-recurrence",
  "reviewed_sha": "32a4bccd837c71f58b72263e641529ffef77b6f8",
  "summary": "The production code for recurrence counting, the merged-fix reopen and Author recovery is correct, but several acceptance criteria are untested or are tested in a different file from the one the ticket names.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/integration/test_retro.py",
      "line": 520,
      "message": "Criterion 2 requires tests/unit/test_retro_recurrence.py to show that a retro reply whose `recurs` names an id not in prior_findings is rejected with a retry finding. That test was written only in the integration file tests/integration/test_retro.py, and tests/unit/test_retro_recurrence.py has no such test.",
      "paved_road": "Add a disk-free test to tests/unit/test_retro_recurrence.py. It should exercise the `recurs` validation (the `validate_recurrences` review hook or the retro stage with fakes) and assert that an unknown `recurs` id produces a `retro_recurs` fail finding and files nothing.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/unit/test_retro_recurrence.py",
      "line": 68,
      "message": "Criterion 3 asks for three unit cases through `Retro.emit_proposals`: (a) a named pending message has `recurrences` 1, not 2, after a second identical call; (b) a message resolved as a merged ticket is reopened as `pending`, with `reopen` true and no resolution; (c) a running-ticket case. `test_emit_counts_each_running_fix_once` covers only (c). Neither the pending case nor the merged-reopen case goes through `emit_proposals` in the unit test.",
      "paved_road": "Extend the emit_proposals unit test, for example by parametrizing it, with a pending message called twice for the same report (assert `recurrences == 1` and zero `enqueue` calls) and a message resolved as a ticket whose journal state is `merged` (assert `pending`, `reopen` true, `resolution` None).",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/unit/test_retro_recurrence.py",
      "line": 51,
      "message": "Criterion 4's first bullet requires a direct call on `Box.record_recurrence` showing that the count rises once per occurrence id, with a repeat of the same id as a no-op. `test_receipt_recovers_both_sides_of_write` uses only one pre-seeded occurrence. No direct call shows the count rising for two distinct occurrence ids, or a fresh call (no seeded intent) with `reopen=True` writing back the merged ticket's message.",
      "paved_road": "Add a direct `Box.record_recurrence` test with a fake FileSystem and MemoryJournal. Call it with occurrence ids 'a', 'a' and 'b' and assert counts 1, 1 and 2. Add a fresh `reopen=True` call on a message resolved as a ticket and assert it is written back `pending`, with `reopen` true and `resolution`/`verdict` None.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/integration/test_retro_box.py",
      "line": 212,
      "message": "Criterion 7's tombstone bullet requires that `reports` rises through the re-report path and that the third report reopens the tombstone as it does today. The parametrized test checks only `reports == 1` after one recurrence and never drives a third report to show the reopen.",
      "paved_road": "Add a tombstone case that emits recurrence proposals from three distinct retro reports, or seeds `reports=2` first. Assert that the third leaves the message `pending`, with `reopen` true and no resolution.",
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
