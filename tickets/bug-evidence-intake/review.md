# Review: snag

Intake can admit a bug ticket whose only evidence file is gitignored, because the check counts that file but the commit path leaves it out.

## Findings

- [logic] chupa/tickets.py:655 `evidence_findings` accepts any regular file on disk, but the staging list comes from `git ls-files --cached --others --exclude-standard`, which omits ignored files. If a host ignores `*.log` (through `.gitignore`, `.git/info/exclude`, or a global excludes file) and the only evidence is `tickets/<stem>/evidence/failure.log`, the check passes. Intake then commits `ticket.md` alone and journals `ticket_intake`, so a bug ticket is admitted with no evidence committed. This hits the ticket's Definition of rejected and its goal of committing evidence with the ticket. The evidence never reaches the commit or a fresh clone, and the Check gate cannot catch it because `_gather_bug` also accepts files in the `ctx.repo` working tree. (do instead: Decide admission from the same set intake commits. For example, list the stem's evidence paths with `ls-files` before admitting, keep only regular non-symlink files, and refuse with the evidence finding if none remain. Alternatively, have the evidence check reject ignored files and say so in the paved road. Add a test where the only evidence file is gitignored: the ticket is refused, nothing is committed, and the files stay on disk.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "43862c04c1583a404dc39f67e59e6135bd2d3a64",
  "stem": "bug-evidence-intake",
  "reviewed_sha": "43862c04c1583a404dc39f67e59e6135bd2d3a64",
  "summary": "Intake can admit a bug ticket whose only evidence file is gitignored, because the check counts that file but the commit path leaves it out.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/tickets.py",
      "line": 655,
      "message": "`evidence_findings` accepts any regular file on disk, but the staging list comes from `git ls-files --cached --others --exclude-standard`, which omits ignored files. If a host ignores `*.log` (through `.gitignore`, `.git/info/exclude`, or a global excludes file) and the only evidence is `tickets/<stem>/evidence/failure.log`, the check passes. Intake then commits `ticket.md` alone and journals `ticket_intake`, so a bug ticket is admitted with no evidence committed. This hits the ticket's Definition of rejected and its goal of committing evidence with the ticket. The evidence never reaches the commit or a fresh clone, and the Check gate cannot catch it because `_gather_bug` also accepts files in the `ctx.repo` working tree.",
      "paved_road": "Decide admission from the same set intake commits. For example, list the stem's evidence paths with `ls-files` before admitting, keep only regular non-symlink files, and refuse with the evidence finding if none remain. Alternatively, have the evidence check reject ignored files and say so in the paved road. Add a test where the only evidence file is gitignored: the ticket is refused, nothing is committed, and the files stay on disk.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
