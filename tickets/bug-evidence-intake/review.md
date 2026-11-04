# Review: snag

The diff exempts journal-settled tickets but re-judges journal-rejected ones, and its widened stray guard admits staged evidence changes that the commit leaves behind, blocking the next intake.

## Findings

- [acceptance] chupa/tickets.py:657 The ticket says the check is never applied to rejected tickets, but the journal exemption covers only {"merged", "already_satisfied"}. `mergequeue.py:383` appends `{"to": "rejected"}` without stamping the frontmatter, so that ticket stays `state: confirmed`. If a stem rejected this way is a bug ticket with no evidence file in the repo, editing its `ticket.md` gets it refused at intake because `evidence_findings` sees neither a rejected frontmatter state nor evidence. `test_settled_bug_is_not_rejudged_for_evidence` covers only frontmatter rejection, so it misses this path. (do instead: Exempt the journal `rejected` state as well, for example `states.get(stem) not in SETTLED | {"rejected"}` using `chupa.status.SETTLED` if the import is safe, otherwise a literal set. Add a parametrized case that journals `{"to": "rejected"}` while the frontmatter stays `confirmed`.)
- [logic] chupa/tickets.py:635 The stray guard now passes any staged entry under a pending stem's `evidence/`, including entries the commit does not carry. A staged deletion or a staged symlink is filtered out of `evidence` by the `ls-files` and `is_file` checks, so `commit --only` leaves it in the index. The stem is no longer pending on the next drain, so that entry counts as stray and `IntakeRefused` blocks intake for every ticket. Before this diff the same entry was refused at once, before any commit. (do instead: Exempt only staged paths that this intake will commit, meaning regular non-symlink files with a non-deletion status. Leave staged deletions and symlinks to the stray refusal, and add a test that a staged evidence deletion is refused up front with nothing committed.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "83db88545a87fac0cb687f71431045b262799707",
  "stem": "bug-evidence-intake",
  "reviewed_sha": "83db88545a87fac0cb687f71431045b262799707",
  "summary": "The diff exempts journal-settled tickets but re-judges journal-rejected ones, and its widened stray guard admits staged evidence changes that the commit leaves behind, blocking the next intake.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/tickets.py",
      "line": 657,
      "message": "The ticket says the check is never applied to rejected tickets, but the journal exemption covers only {\"merged\", \"already_satisfied\"}. `mergequeue.py:383` appends `{\"to\": \"rejected\"}` without stamping the frontmatter, so that ticket stays `state: confirmed`. If a stem rejected this way is a bug ticket with no evidence file in the repo, editing its `ticket.md` gets it refused at intake because `evidence_findings` sees neither a rejected frontmatter state nor evidence. `test_settled_bug_is_not_rejudged_for_evidence` covers only frontmatter rejection, so it misses this path.",
      "paved_road": "Exempt the journal `rejected` state as well, for example `states.get(stem) not in SETTLED | {\"rejected\"}` using `chupa.status.SETTLED` if the import is safe, otherwise a literal set. Add a parametrized case that journals `{\"to\": \"rejected\"}` while the frontmatter stays `confirmed`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/tickets.py",
      "line": 635,
      "message": "The stray guard now passes any staged entry under a pending stem's `evidence/`, including entries the commit does not carry. A staged deletion or a staged symlink is filtered out of `evidence` by the `ls-files` and `is_file` checks, so `commit --only` leaves it in the index. The stem is no longer pending on the next drain, so that entry counts as stray and `IntakeRefused` blocks intake for every ticket. Before this diff the same entry was refused at once, before any commit.",
      "paved_road": "Exempt only staged paths that this intake will commit, meaning regular non-symlink files with a non-deletion status. Leave staged deletions and symlinks to the stray refusal, and add a test that a staged evidence deletion is refused up front with nothing committed.",
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
