# Review: snag

The triage code paths look plausible, but tests/test_triage.py has only one test, so the behaviors that acceptance criteria 3, 4 and 5 require it to prove are not tested.

## Findings

- [acceptance] tests/test_triage.py:41 AC3 is only partly covered. The second pass checks that no new request is made, but no test re-records the author verdict at a stale `produced_by_spec_version` and checks that it resolves as a `decision` record without a request. (do instead: Add a test that calls `box.record_verdict(third, Verdict(verdict='author', produced_by_spec_version='0.9', ...))`, runs `main(['triage'])`, and asserts there is no new request, `decision-<third>` is committed, and the message is `resolved`.)
- [acceptance] tests/test_triage.py:16 No test covers AC4's fail-closed cases: (a) a tombstone whose link resolves nowhere writes a `decision` record, (b) a record already committed for a pending message resolves it with zero requests, and (c) a reply that stays invalid through every re-prompt leaves the message pending and adds no commit. (do instead: Add one test for each of the three cases. Assert the record kind and link, the request count, the message status, and that `git log` gains no `chupa(decisions):` commit in case (c).)
- [acceptance] tests/test_triage.py:16 AC5 requires a test that the `triage` verb exits 2 while another process holds the lock. No such test exists. (do instead: Acquire a `Lockfile` on the state dir from the test (as the existing run/drain contention tests do). Then assert `main(['triage'], ...) == 2`, that no requests were made, and that no `triage_pass` signal was journaled.)
- [acceptance] tests/test_triage.py:31 AC2 requires the committed records to parse through `parse_record` with the right kind, link and `reopen_after_days`. The test reads them through `read_registry` and checks only `link`. It never checks kind or `reopen_after_days`, and never confirms that exactly two `chupa(decisions): <id>` commits were added. `parse_record` is imported but never used. (do instead: Assert that `git log` subjects contain exactly `chupa(decisions): tombstone-<first>` and `chupa(decisions): decision-<second>`. Parse each committed file with `parse_record` and assert its `kind`, `link`, and `reopen_after_days == 30`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "9b9152dec886748ec7afaec0408508ad1976f621",
  "stem": "box-triage",
  "reviewed_sha": "9b9152dec886748ec7afaec0408508ad1976f621",
  "summary": "The triage code paths look plausible, but tests/test_triage.py has only one test, so the behaviors that acceptance criteria 3, 4 and 5 require it to prove are not tested.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_triage.py",
      "line": 41,
      "message": "AC3 is only partly covered. The second pass checks that no new request is made, but no test re-records the author verdict at a stale `produced_by_spec_version` and checks that it resolves as a `decision` record without a request.",
      "paved_road": "Add a test that calls `box.record_verdict(third, Verdict(verdict='author', produced_by_spec_version='0.9', ...))`, runs `main(['triage'])`, and asserts there is no new request, `decision-<third>` is committed, and the message is `resolved`."
    },
    {
      "code": "acceptance",
      "path": "tests/test_triage.py",
      "line": 16,
      "message": "No test covers AC4's fail-closed cases: (a) a tombstone whose link resolves nowhere writes a `decision` record, (b) a record already committed for a pending message resolves it with zero requests, and (c) a reply that stays invalid through every re-prompt leaves the message pending and adds no commit.",
      "paved_road": "Add one test for each of the three cases. Assert the record kind and link, the request count, the message status, and that `git log` gains no `chupa(decisions):` commit in case (c)."
    },
    {
      "code": "acceptance",
      "path": "tests/test_triage.py",
      "line": 16,
      "message": "AC5 requires a test that the `triage` verb exits 2 while another process holds the lock. No such test exists.",
      "paved_road": "Acquire a `Lockfile` on the state dir from the test (as the existing run/drain contention tests do). Then assert `main(['triage'], ...) == 2`, that no requests were made, and that no `triage_pass` signal was journaled."
    },
    {
      "code": "acceptance",
      "path": "tests/test_triage.py",
      "line": 31,
      "message": "AC2 requires the committed records to parse through `parse_record` with the right kind, link and `reopen_after_days`. The test reads them through `read_registry` and checks only `link`. It never checks kind or `reopen_after_days`, and never confirms that exactly two `chupa(decisions): <id>` commits were added. `parse_record` is imported but never used.",
      "paved_road": "Assert that `git log` subjects contain exactly `chupa(decisions): tombstone-<first>` and `chupa(decisions): decision-<second>`. Parse each committed file with `parse_record` and assert its `kind`, `link`, and `reopen_after_days == 30`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
