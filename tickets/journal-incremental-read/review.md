# Review: snag

Incremental read and the pure helper are correct, but append() now runs the full read_segments() over every segment, so a fresh instance's first append parses the whole journal, not just the active segment, and one acceptance comparison is only partly tested.

## Findings

- [acceptance] chupa/journal.py:183 append() calls `list(self.read_segments())[-1]`, which goes through every segment. On a fresh instance, the first append() fully parses every rolled segment, not just the active one. The ticket says 'a fresh instance's first `append()` parses the active segment once'. With 12 segments and 24k events, a short-lived process that only appends now pays the full-journal parse that base never paid. Every later append() also stats every rolled segment and copies each segment's cached events into a tuple, which is O(total events) per write. It also makes writes fail whenever any rolled segment is corrupt, which base append() never checked. (do instead: Make append() check only the active segment through the instance's incremental read. For example, factor the active-segment branch of read_segments() into a method that takes one path, updates self._cache[path] and returns its events. Call it with `segment` in append() and use its first event's ts for the roll-age check. Leave rolled segments alone on the write path.)
- [acceptance] tests/integration/test_journal_incremental.py:34 Acceptance criterion 2 says that after k appends by the same instance, the next read()'s result equals a fresh Journal's read(), compared by value and order. For the same-instance case, the test compares only the `body['n']` values against range(7). It never compares the full events to a fresh `Journal(tmp_path, clock).read()`. Only the second-writer case does that. (do instead: In the same-instance case, capture the read() result and assert it equals `Journal(tmp_path, clock).read()`, as the test already does for the second-writer case.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "c1a5ecae62daee42b5b6288724df45a5aea2d0e3",
  "stem": "journal-incremental-read",
  "reviewed_sha": "c1a5ecae62daee42b5b6288724df45a5aea2d0e3",
  "summary": "Incremental read and the pure helper are correct, but append() now runs the full read_segments() over every segment, so a fresh instance's first append parses the whole journal, not just the active segment, and one acceptance comparison is only partly tested.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/journal.py",
      "line": 183,
      "message": "append() calls `list(self.read_segments())[-1]`, which goes through every segment. On a fresh instance, the first append() fully parses every rolled segment, not just the active one. The ticket says 'a fresh instance's first `append()` parses the active segment once'. With 12 segments and 24k events, a short-lived process that only appends now pays the full-journal parse that base never paid. Every later append() also stats every rolled segment and copies each segment's cached events into a tuple, which is O(total events) per write. It also makes writes fail whenever any rolled segment is corrupt, which base append() never checked.",
      "paved_road": "Make append() check only the active segment through the instance's incremental read. For example, factor the active-segment branch of read_segments() into a method that takes one path, updates self._cache[path] and returns its events. Call it with `segment` in append() and use its first event's ts for the roll-age check. Leave rolled segments alone on the write path.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/integration/test_journal_incremental.py",
      "line": 34,
      "message": "Acceptance criterion 2 says that after k appends by the same instance, the next read()'s result equals a fresh Journal's read(), compared by value and order. For the same-instance case, the test compares only the `body['n']` values against range(7). It never compares the full events to a fresh `Journal(tmp_path, clock).read()`. Only the second-writer case does that.",
      "paved_road": "In the same-instance case, capture the read() result and assert it equals `Journal(tmp_path, clock).read()`, as the test already does for the second-writer case.",
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
