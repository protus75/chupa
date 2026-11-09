# Review: snag

The lock split, the review-slot orphan filter and the tests meet the acceptance criteria, but the state-directory file table in docs/how-chupa-works.md section 10.1 does not list the new journal.lock file and still calls chupa.lock the single-writer lock.

## Findings

- [acceptance] docs/how-chupa-works.md:- Section 10.1 'Files' lists everything that lives under state_dir and says "`chupa.lock` | The single-writer lock." After this diff, Journal.append creates `<state_dir>/journal.lock` and takes an exclusive flock on it for every append. That file is missing from the table, and chupa.lock no longer guards journal writes. The diff even updates test_storm_producer to expect journal.lock in the state-dir listing, yet the documented listing still describes the old layout. (do instead: Add a `journal.lock` row to the section 10.1 table: a short-held exclusive flock taken by every journal append, covering torn-tail repair, segment roll and the write. Reword the `chupa.lock` row so it says the lock guards checkout and git writes to main, not journal appends.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5a8fa2522cdbef5be09889216240fe1e0e98eb9a",
  "stem": "review-lock-only-for-intake",
  "reviewed_sha": "5a8fa2522cdbef5be09889216240fe1e0e98eb9a",
  "summary": "The lock split, the review-slot orphan filter and the tests meet the acceptance criteria, but the state-directory file table in docs/how-chupa-works.md section 10.1 does not list the new journal.lock file and still calls chupa.lock the single-writer lock.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "Section 10.1 'Files' lists everything that lives under state_dir and says \"`chupa.lock` | The single-writer lock.\" After this diff, Journal.append creates `<state_dir>/journal.lock` and takes an exclusive flock on it for every append. That file is missing from the table, and chupa.lock no longer guards journal writes. The diff even updates test_storm_producer to expect journal.lock in the state-dir listing, yet the documented listing still describes the old layout.",
      "paved_road": "Add a `journal.lock` row to the section 10.1 table: a short-held exclusive flock taken by every journal append, covering torn-tail repair, segment roll and the write. Reword the `chupa.lock` row so it says the lock guards checkout and git writes to main, not journal appends.",
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
