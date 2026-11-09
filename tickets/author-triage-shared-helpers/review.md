# Review: approve

The diff leaves one public copy each of goal, commit_record, committed and list_open_tickets in chupa/author.py. Triage imports them from author at every former call site. The listing uses triage's semantics: it lists tickets on disk, committed at HEAD and not merged, using last_states. The new integration, unit and reproducer tests meet every acceptance criterion inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "8361a993b4349bb251321b03811ad6c290ad950a",
  "stem": "author-triage-shared-helpers",
  "reviewed_sha": "8361a993b4349bb251321b03811ad6c290ad950a",
  "summary": "The diff leaves one public copy each of goal, commit_record, committed and list_open_tickets in chupa/author.py. Triage imports them from author at every former call site. The listing uses triage's semantics: it lists tickets on disk, committed at HEAD and not merged, using last_states. The new integration, unit and reproducer tests meet every acceptance criterion inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
