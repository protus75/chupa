# Review: snag

The Author stage is wired, but tests/test_author.py covers only the happy path, so acceptance criteria 3 and 4 are unproven, and the test_triage changes delete the stale-version assertions instead of keeping them.

## Findings

- [acceptance] tests/test_author.py:12 Acceptance criterion 3 is unmet. tests/test_author.py has one test, the happy path. No test covers an author reply that names an existing stem, or one that fails `validate_ticket`, being re-prompted with the findings. No test shows that running out of the allowance commits no ticket and resolves the message with one `decision-<id>` record. (do instead: Add FakeLLM-driven tests through `main(["triage"])`. One sends an author reply whose stem already exists under tickets/ and one that fails `validate_ticket`; assert the second author request's `retry_findings` contains those findings. One sends invalid replies until the allowance runs out; assert no `chupa(<stem>): ticket` commit, one `chupa(decisions): decision-<id>` commit, and the resolution `{kind: decision, link: decision-<id>}`.)
- [acceptance] tests/test_author.py:12 Acceptance criterion 4 is unmet. No test shows that a `bug_report` message missing `has_repro` gets the failure decision record with zero author requests. No test shows the same for a message whose journal already carries an `author_invoked` signal. (do instead: Add both tests. Enqueue a `bug_report` with no `has_repro` and assert that only the triage request was made and a `decision-<id>` record was committed. Separately, record an `author` verdict at the current spec version, append `{"signal": "author_invoked", "message": <id>}` to the journal, run triage, and assert zero requests and a committed `decision-<id>` record.)
- [acceptance] tests/test_triage.py:115 The diff deletes the stale-version assertions: re-recording the author verdict at version 0.9, then expecting zero new requests, a `decision-<id>` commit, and a record body naming both 0.9 and 1.0. Criterion 5 requires every assertion other than the author-verdict expectations to stay unchanged, and the ticket says the stale-version rule is unchanged. The diff removes the rule's coverage. (do instead: Keep the stale-version check. Enqueue a fresh pending message, record an `author` verdict for it with `produced_by_spec_version="0.9"`, run triage, and restore the original assertions (no new LLM request, `chupa(decisions): decision-<id>` at HEAD, record kind `decision` with both "0.9" and "1.0" in the body).)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "069507224e5ed8b5973192f90169158f8cb435b2",
  "stem": "author-stage",
  "reviewed_sha": "069507224e5ed8b5973192f90169158f8cb435b2",
  "summary": "The Author stage is wired, but tests/test_author.py covers only the happy path, so acceptance criteria 3 and 4 are unproven, and the test_triage changes delete the stale-version assertions instead of keeping them.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_author.py",
      "line": 12,
      "message": "Acceptance criterion 3 is unmet. tests/test_author.py has one test, the happy path. No test covers an author reply that names an existing stem, or one that fails `validate_ticket`, being re-prompted with the findings. No test shows that running out of the allowance commits no ticket and resolves the message with one `decision-<id>` record.",
      "paved_road": "Add FakeLLM-driven tests through `main([\"triage\"])`. One sends an author reply whose stem already exists under tickets/ and one that fails `validate_ticket`; assert the second author request's `retry_findings` contains those findings. One sends invalid replies until the allowance runs out; assert no `chupa(<stem>): ticket` commit, one `chupa(decisions): decision-<id>` commit, and the resolution `{kind: decision, link: decision-<id>}`."
    },
    {
      "code": "acceptance",
      "path": "tests/test_author.py",
      "line": 12,
      "message": "Acceptance criterion 4 is unmet. No test shows that a `bug_report` message missing `has_repro` gets the failure decision record with zero author requests. No test shows the same for a message whose journal already carries an `author_invoked` signal.",
      "paved_road": "Add both tests. Enqueue a `bug_report` with no `has_repro` and assert that only the triage request was made and a `decision-<id>` record was committed. Separately, record an `author` verdict at the current spec version, append `{\"signal\": \"author_invoked\", \"message\": <id>}` to the journal, run triage, and assert zero requests and a committed `decision-<id>` record."
    },
    {
      "code": "acceptance",
      "path": "tests/test_triage.py",
      "line": 115,
      "message": "The diff deletes the stale-version assertions: re-recording the author verdict at version 0.9, then expecting zero new requests, a `decision-<id>` commit, and a record body naming both 0.9 and 1.0. Criterion 5 requires every assertion other than the author-verdict expectations to stay unchanged, and the ticket says the stale-version rule is unchanged. The diff removes the rule's coverage.",
      "paved_road": "Keep the stale-version check. Enqueue a fresh pending message, record an `author` verdict for it with `produced_by_spec_version=\"0.9\"`, run triage, and restore the original assertions (no new LLM request, `chupa(decisions): decision-<id>` at HEAD, record kind `decision` with both \"0.9\" and \"1.0\" in the body)."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
