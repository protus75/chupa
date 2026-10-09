# Review: snag

Most of the chain is in place, but a reopened message that triage tombstones against any link other than its own old record overwrites its committed tombstone record, which breaks the reopen invariant.

## Findings

- [logic] chupa/triage.py:212 For a reopened message, the diff rewrites only the tombstone verdict whose link is `tombstone-{message.id}` into author (line ~182). Any other tombstone verdict, for example back to the original target `known`, still reaches `_record`. `_record` uses the fixed record_id `tombstone-{message.id}`, so it overwrites the committed `tombstones/tombstone-{id}` file with new bytes. Its `_commit_record` effect key `ticket-plane/decisions/tombstone-{id}` already completed, so it replays as a no-op. The result is an uncommitted, diverged registry file in the working tree, and the box is resolved back to a tombstone. This breaks 'preserves committed registry bytes' and 'recovery without re-tombstoning', and `RereportJournal.record` then orders arrivals against the stale tombstone completion. (do instead: When `message.reopen` is true, never let `_record` write `tombstone-{message.id}` again. Route every tombstone verdict for a reopened message to author, or to a decision record with a fresh id, so the committed registry bytes stay unchanged. Add a test to test_reopened_message_bypasses_its_tombstone where the scripted triage reply tombstones to another committed link, and assert that the record bytes and HEAD are unchanged.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e9806b97250fb8c0a249ab55b5433b7a5ec32295",
  "stem": "retro-box-activation",
  "reviewed_sha": "e9806b97250fb8c0a249ab55b5433b7a5ec32295",
  "summary": "Most of the chain is in place, but a reopened message that triage tombstones against any link other than its own old record overwrites its committed tombstone record, which breaks the reopen invariant.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/triage.py",
      "line": 212,
      "message": "For a reopened message, the diff rewrites only the tombstone verdict whose link is `tombstone-{message.id}` into author (line ~182). Any other tombstone verdict, for example back to the original target `known`, still reaches `_record`. `_record` uses the fixed record_id `tombstone-{message.id}`, so it overwrites the committed `tombstones/tombstone-{id}` file with new bytes. Its `_commit_record` effect key `ticket-plane/decisions/tombstone-{id}` already completed, so it replays as a no-op. The result is an uncommitted, diverged registry file in the working tree, and the box is resolved back to a tombstone. This breaks 'preserves committed registry bytes' and 'recovery without re-tombstoning', and `RereportJournal.record` then orders arrivals against the stale tombstone completion.",
      "paved_road": "When `message.reopen` is true, never let `_record` write `tombstone-{message.id}` again. Route every tombstone verdict for a reopened message to author, or to a decision record with a fresh id, so the committed registry bytes stay unchanged. Add a test to test_reopened_message_bypasses_its_tombstone where the scripted triage reply tombstones to another committed link, and assert that the record bytes and HEAD are unchanged.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
