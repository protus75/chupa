# Review: approve

Git.commit now stages its `only` paths with update-index, raises NothingToCommit when they already match HEAD, and returns the new sha; merge_squash commits and returns the sha; every in-fence caller drops its own add and rev_parse except the add in restore_publication, which the ticket keeps; intake skips a ticket another process already committed; and the unit, integration and fake updates cover every acceptance criterion.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0feb113e81109dfda46fe175594d0c0617885afe",
  "stem": "git-commit-returns-sha",
  "reviewed_sha": "0feb113e81109dfda46fe175594d0c0617885afe",
  "summary": "Git.commit now stages its `only` paths with update-index, raises NothingToCommit when they already match HEAD, and returns the new sha; merge_squash commits and returns the sha; every in-fence caller drops its own add and rev_parse except the add in restore_publication, which the ticket keeps; intake skips a ticket another process already committed; and the unit, integration and fake updates cover every acceptance criterion.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
