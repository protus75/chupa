# Review: rma

Both prior findings are fixed and the diff is otherwise correct, but acceptance criterion 2 says the next read() after k same-instance appends parses exactly k lines, and the ticket's own Scope-in rules out that count for any k >= 2.

## Findings

- [ticket] tests/integration/test_journal_incremental.py:45 Acceptance criterion 2 says that after k appends by the same instance, the next read() parses exactly k lines. Scope-in requires append() to check the active segment through the instance's own incremental read, parsing only lines it has not cached. It also forbids any in-process shortcut for the instance's own appends. And the mandated section 10 sentence says an instance parses each byte of the journal once. With one shared cache, each append after the first parses the line the previous append wrote, so the next read() parses only the last line: 1, not k. The test pins this with `assert len(calls) == 1` for k=3. The only way to get exactly k is a second, append-only cache that parses those lines again. That breaks the 'each byte once' doc statement the ticket requires, and it is the defensive dual path CLAUDE.md bans. For k >= 2, criterion 2 cannot hold together with Scope-in. (do instead: Change criterion 2's same-instance case to say: the next read() parses only lines this instance has not yet parsed, at most k, and exactly 1 when every append came from this instance after its last read. Keep 'exactly k' for appends by a second Journal. Then re-run Review on the current diff, which already meets that wording.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5fa6fe1d9110a24e6ada3a9b2b95290d9ad3ba16",
  "stem": "journal-incremental-read",
  "reviewed_sha": "5fa6fe1d9110a24e6ada3a9b2b95290d9ad3ba16",
  "summary": "Both prior findings are fixed and the diff is otherwise correct, but acceptance criterion 2 says the next read() after k same-instance appends parses exactly k lines, and the ticket's own Scope-in rules out that count for any k >= 2.",
  "findings": [
    {
      "code": "ticket",
      "path": "tests/integration/test_journal_incremental.py",
      "line": 45,
      "message": "Acceptance criterion 2 says that after k appends by the same instance, the next read() parses exactly k lines. Scope-in requires append() to check the active segment through the instance's own incremental read, parsing only lines it has not cached. It also forbids any in-process shortcut for the instance's own appends. And the mandated section 10 sentence says an instance parses each byte of the journal once. With one shared cache, each append after the first parses the line the previous append wrote, so the next read() parses only the last line: 1, not k. The test pins this with `assert len(calls) == 1` for k=3. The only way to get exactly k is a second, append-only cache that parses those lines again. That breaks the 'each byte once' doc statement the ticket requires, and it is the defensive dual path CLAUDE.md bans. For k >= 2, criterion 2 cannot hold together with Scope-in.",
      "paved_road": "Change criterion 2's same-instance case to say: the next read() parses only lines this instance has not yet parsed, at most k, and exactly 1 when every append came from this instance after its last read. Keep 'exactly k' for appends by a second Journal. Then re-run Review on the current diff, which already meets that wording.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "rma"
}
```
