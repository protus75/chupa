# Review: snag

The seed review, lift and merge re-check are wired as the ticket asks, but the acceptance-5 test cannot catch the bug it targets, and the merge gate checks main's working-tree files instead of main's committed files.

## Findings

- [acceptance] tests/test_stages.py:237 `test_non_seeding_worktree_ticket_is_neither_reviewed_nor_lifted` uses `agent()`, which commits the foreign `tickets/foreign-ticket/ticket.md`. The `scope_fence` gate then fails Check before seed handling runs. If the `"tickets" in ticket.scope_fence` guard were removed, the test would still pass, so it does not prove acceptance criterion 5. (do instead: Leave the foreign ticket.md uncommitted in the worktree (write it without `git add`/commit) so every mechanical Check gate passes. Then assert that Check is `ok`, `seeds == []`, there is no `requisition_review` request, and no seed was lifted to main.)
- [logic] chupa/merge.py:186 The MERGE-SAFETY inputs read the seed text (`ctx.repo / path`) and `checks.json` (`ctx.repo / TICKETS_DIR / stem / "checks.json"`) from the main checkout's working tree. Only the blob SHA comes from `main:<path>`. An uncommitted edit in the shared checkout (ticket-file authoring there is a sanctioned path) can change the approvals or the text that gets validated, so the gate does not re-check what main actually commits. (do instead: Read both the seed text and `checks.json` from main's committed tree through `git.py` (`main:<path>`), so that the SHA, the validated text and the recorded approvals all come from the same commit.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0cfefc42eba8136151754de9737589a47626f3d5",
  "stem": "requisition-seed-path",
  "reviewed_sha": "0cfefc42eba8136151754de9737589a47626f3d5",
  "summary": "The seed review, lift and merge re-check are wired as the ticket asks, but the acceptance-5 test cannot catch the bug it targets, and the merge gate checks main's working-tree files instead of main's committed files.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": 237,
      "message": "`test_non_seeding_worktree_ticket_is_neither_reviewed_nor_lifted` uses `agent()`, which commits the foreign `tickets/foreign-ticket/ticket.md`. The `scope_fence` gate then fails Check before seed handling runs. If the `\"tickets\" in ticket.scope_fence` guard were removed, the test would still pass, so it does not prove acceptance criterion 5.",
      "paved_road": "Leave the foreign ticket.md uncommitted in the worktree (write it without `git add`/commit) so every mechanical Check gate passes. Then assert that Check is `ok`, `seeds == []`, there is no `requisition_review` request, and no seed was lifted to main."
    },
    {
      "code": "logic",
      "path": "chupa/merge.py",
      "line": 186,
      "message": "The MERGE-SAFETY inputs read the seed text (`ctx.repo / path`) and `checks.json` (`ctx.repo / TICKETS_DIR / stem / \"checks.json\"`) from the main checkout's working tree. Only the blob SHA comes from `main:<path>`. An uncommitted edit in the shared checkout (ticket-file authoring there is a sanctioned path) can change the approvals or the text that gets validated, so the gate does not re-check what main actually commits.",
      "paved_road": "Read both the seed text and `checks.json` from main's committed tree through `git.py` (`main:<path>`), so that the SHA, the validated text and the recorded approvals all come from the same commit."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
