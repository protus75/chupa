# Review: snag

The diff meets the ticket's criteria and fixes the earlier finding: the engine-verb decision is now driven through the real `_control`, `_verdict` and `_retro` paths. One problem remains: the new unit test's verdict route still reads the filesystem.

## Findings

- [logic] tests/unit/test_lock_holder.py:34 The `verdict` route calls the real `_verdict` with `journal.read` returning `[]` and `repo=Path("repo")`. As a result `reject_queue(history).get(stem)` is None, and `_verdict` runs `(checkout.repo / ticket_path(stem)).is_file()`. That is a real stat of `repo/tickets/candidate/ticket.md` relative to the process cwd. So a test in `tests/unit/`, which the ticket requires to be fake-backed, reads disk. Its preview branch depends on which directory pytest runs from. (do instead: Keep the verdict route off the filesystem. One way is to pass a fake `repo` whose `/` returns an object with `is_file()` returning False. Another is to have `checkout.journal.read` return history that puts `candidate` in the reject queue, so `_verdict` takes the `queued` preview branch and never touches a path.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "7802c119e1cd6e08793c3abc7b22661c19103af3",
  "stem": "verb-lock-need-single-source",
  "reviewed_sha": "7802c119e1cd6e08793c3abc7b22661c19103af3",
  "summary": "The diff meets the ticket's criteria and fixes the earlier finding: the engine-verb decision is now driven through the real `_control`, `_verdict` and `_retro` paths. One problem remains: the new unit test's verdict route still reads the filesystem.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/unit/test_lock_holder.py",
      "line": 34,
      "message": "The `verdict` route calls the real `_verdict` with `journal.read` returning `[]` and `repo=Path(\"repo\")`. As a result `reject_queue(history).get(stem)` is None, and `_verdict` runs `(checkout.repo / ticket_path(stem)).is_file()`. That is a real stat of `repo/tickets/candidate/ticket.md` relative to the process cwd. So a test in `tests/unit/`, which the ticket requires to be fake-backed, reads disk. Its preview branch depends on which directory pytest runs from.",
      "paved_road": "Keep the verdict route off the filesystem. One way is to pass a fake `repo` whose `/` returns an object with `is_file()` returning False. Another is to have `checkout.journal.read` return history that puts `candidate` in the reject queue, so `_verdict` takes the `queued` preview branch and never touches a path.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
