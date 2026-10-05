# Review: snag

The diff meets the acceptance criteria, but when the ticket commit fails it leaves the authored ticket.md written (and possibly staged) in the working tree while it resolves the message as a decision.

## Findings

- [logic] chupa/author.py:167 `author()` writes `tickets/<stem>/ticket.md` through the fs seam before `_commit`. If `git add`/`git commit` (or anything after the write) raises, the broad `except` resolves the message as `decision-<id>`, but the uncommitted, already-stamped ticket file stays in the working tree and may be staged in the index. Working-tree ticket files are the sanctioned intake path, so a later intake would admit this ticket even though the box message records 'no ticket'. That is a second route by which an Author-produced ticket lands, and the state is corrupt on the failure path. (do instead: On any failure after the write, remove the written ticket file and unstage it before calling `_decision`. Go through the fs seam and a `git.py` op (for example, restore or reset that one path through an argv wrapper), and add a test in which the commit effect raises and the test asserts that no `tickets/<stem>/` remains and the index is clean.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "c4a7b2e03a349c98d6839718ecd0427ff03647e3",
  "stem": "author-stage",
  "reviewed_sha": "c4a7b2e03a349c98d6839718ecd0427ff03647e3",
  "summary": "The diff meets the acceptance criteria, but when the ticket commit fails it leaves the authored ticket.md written (and possibly staged) in the working tree while it resolves the message as a decision.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/author.py",
      "line": 167,
      "message": "`author()` writes `tickets/<stem>/ticket.md` through the fs seam before `_commit`. If `git add`/`git commit` (or anything after the write) raises, the broad `except` resolves the message as `decision-<id>`, but the uncommitted, already-stamped ticket file stays in the working tree and may be staged in the index. Working-tree ticket files are the sanctioned intake path, so a later intake would admit this ticket even though the box message records 'no ticket'. That is a second route by which an Author-produced ticket lands, and the state is corrupt on the failure path.",
      "paved_road": "On any failure after the write, remove the written ticket file and unstage it before calling `_decision`. Go through the fs seam and a `git.py` op (for example, restore or reset that one path through an argv wrapper), and add a test in which the commit effect raises and the test asserts that no `tickets/<stem>/` remains and the index is clean."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
