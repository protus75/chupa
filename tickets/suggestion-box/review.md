# Review: snag

Most of the diff is correct, but `normalize` keeps an empty string for every token that was all digits, so the result has double spaces and two reasons that should share a signature do not.

## Findings

- [logic] chupa/box.py:107 `normalize` removes digits from each token, then joins every token with a space, including tokens that are now empty. A digit-only token in the middle leaves a double space, so `normalize('line 42 failed')` returns `'line  failed'`, not `'line failed'`. The ticket says normalize collapses whitespace to single spaces. Because the signature hashes this string, `'a 42 b'` and `'a b'` get different signatures, and dedup misses two messages that differ only by a line number. The test misses this because both of its reasons put the number in the same place. (do instead: Remove the `/` tokens, remove the digit runs, then collapse whitespace: `' '.join(re.sub(r'\d+', '', ' '.join(t for t in reason.split() if '/' not in t)).split())`. Add a test that `normalize('a 42 b') == normalize('a b') == 'a b'`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5459546bc0acede0a7ddba043561559d716b08ea",
  "stem": "suggestion-box",
  "reviewed_sha": "5459546bc0acede0a7ddba043561559d716b08ea",
  "summary": "Most of the diff is correct, but `normalize` keeps an empty string for every token that was all digits, so the result has double spaces and two reasons that should share a signature do not.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/box.py",
      "line": 107,
      "message": "`normalize` removes digits from each token, then joins every token with a space, including tokens that are now empty. A digit-only token in the middle leaves a double space, so `normalize('line 42 failed')` returns `'line  failed'`, not `'line failed'`. The ticket says normalize collapses whitespace to single spaces. Because the signature hashes this string, `'a 42 b'` and `'a b'` get different signatures, and dedup misses two messages that differ only by a line number. The test misses this because both of its reasons put the number in the same place.",
      "paved_road": "Remove the `/` tokens, remove the digit runs, then collapse whitespace: `' '.join(re.sub(r'\\d+', '', ' '.join(t for t in reason.split() if '/' not in t)).split())`. Add a test that `normalize('a 42 b') == normalize('a b') == 'a b'`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
