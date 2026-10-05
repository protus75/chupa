# Review: snag

The stage and its wiring are mostly correct, but `open_tickets` lists merged and uncommitted tickets, and the tests that acceptance criteria 3 and 4 require are missing.

## Findings

- [acceptance] chupa/author.py:86 The ticket says `open_tickets` lists each committed non-merged stem. This loop globs every `tickets/*/ticket.md` in the working tree, so it also lists merged tickets and uncommitted files. `chupa/triage.py` filters both out with `stem not in merged` and `_committed(...)`. (do instead: Build the list the way `triage_pass` does: skip stems whose folded state is `merged` and include only paths committed on main.)
- [acceptance] tests/test_author.py:41 Criterion 3 is only partly met. The tests cover a reply that fails `validate_ticket`, but no test sends a reply naming an existing stem (an existing `tickets/<stem>/` or a stem named in a journal event) and asserts it re-prompts with the stem-reuse finding. (do instead: Add a test whose first author reply names an already-committed stem. Assert that the second author request's rendered prompt carries the 'already used' finding and that a valid second reply commits.)
- [acceptance] tests/test_author.py:41 Criterion 4 is unmet. No test sends a `bug_report` message missing `has_repro` and asserts a `decision-<id>` record with zero author requests. No test sets up a pending message whose journal carries `author_invoked` and asserts the decision record with zero requests. (do instead: Add both tests to `tests/test_author.py`. In each, drive `main(["triage"])` and assert the message resolves to `decision-<id>`, the record commits, and `llm.requests` holds no `author` surface request.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a19903f1c9db33fb6e876c786bc7f07e85fceedf",
  "stem": "author-stage",
  "reviewed_sha": "a19903f1c9db33fb6e876c786bc7f07e85fceedf",
  "summary": "The stage and its wiring are mostly correct, but `open_tickets` lists merged and uncommitted tickets, and the tests that acceptance criteria 3 and 4 require are missing.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/author.py",
      "line": 86,
      "message": "The ticket says `open_tickets` lists each committed non-merged stem. This loop globs every `tickets/*/ticket.md` in the working tree, so it also lists merged tickets and uncommitted files. `chupa/triage.py` filters both out with `stem not in merged` and `_committed(...)`.",
      "paved_road": "Build the list the way `triage_pass` does: skip stems whose folded state is `merged` and include only paths committed on main."
    },
    {
      "code": "acceptance",
      "path": "tests/test_author.py",
      "line": 41,
      "message": "Criterion 3 is only partly met. The tests cover a reply that fails `validate_ticket`, but no test sends a reply naming an existing stem (an existing `tickets/<stem>/` or a stem named in a journal event) and asserts it re-prompts with the stem-reuse finding.",
      "paved_road": "Add a test whose first author reply names an already-committed stem. Assert that the second author request's rendered prompt carries the 'already used' finding and that a valid second reply commits."
    },
    {
      "code": "acceptance",
      "path": "tests/test_author.py",
      "line": 41,
      "message": "Criterion 4 is unmet. No test sends a `bug_report` message missing `has_repro` and asserts a `decision-<id>` record with zero author requests. No test sets up a pending message whose journal carries `author_invoked` and asserts the decision record with zero requests.",
      "paved_road": "Add both tests to `tests/test_author.py`. In each, drive `main([\"triage\"])` and assert the message resolves to `decision-<id>`, the record commits, and `llm.requests` holds no `author` surface request."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
