# Review: snag

The seed candidate filter treats every tracked ticket that is identical to main as an existing foreign stem, so a seeding Check fails in any repo that already holds other tickets.

## Findings

- [logic] chupa/stages.py:682 `_review_seeds` globs every `tickets/*/ticket.md` in the worktree. The worktree is created from main by `worktree_add(..., MAIN)`, so it holds every ticket already committed on main. The code never drops files that match main. Any ticket on main that this stem did not seed (main_sha == sha, seed not in own) hits `main_sha is not None and (main_sha != sha or seed not in own)` and becomes a `snag` with 'already exists on main'. In a real repo with other tickets, every seeding ticket therefore fails Check with `gate_failed`. The tests miss this only because their fixture repos hold no other tickets on main. The ticket says candidates are only files that are 'untracked or differ from main'. (do instead: Before any other classification, skip a worktree ticket whose blob SHA equals main's blob SHA and that is not one of this stem's journaled seeds, so it is not a candidate at all. Add a test where main already holds an unrelated ticket and a seeding run still passes with only its new seeds reviewed.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "ef47a141e619976c53ff1baaf831ab8de7a54441",
  "stem": "requisition-seed-path",
  "reviewed_sha": "ef47a141e619976c53ff1baaf831ab8de7a54441",
  "summary": "The seed candidate filter treats every tracked ticket that is identical to main as an existing foreign stem, so a seeding Check fails in any repo that already holds other tickets.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 682,
      "message": "`_review_seeds` globs every `tickets/*/ticket.md` in the worktree. The worktree is created from main by `worktree_add(..., MAIN)`, so it holds every ticket already committed on main. The code never drops files that match main. Any ticket on main that this stem did not seed (main_sha == sha, seed not in own) hits `main_sha is not None and (main_sha != sha or seed not in own)` and becomes a `snag` with 'already exists on main'. In a real repo with other tickets, every seeding ticket therefore fails Check with `gate_failed`. The tests miss this only because their fixture repos hold no other tickets on main. The ticket says candidates are only files that are 'untracked or differ from main'.",
      "paved_road": "Before any other classification, skip a worktree ticket whose blob SHA equals main's blob SHA and that is not one of this stem's journaled seeds, so it is not a candidate at all. Add a test where main already holds an unrelated ticket and a seeding run still passes with only its new seeds reviewed."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
