# Review: snag

Author copies report evidence into the repo working tree from inside the gate, before validation, and never removes it when an attempt is rejected or Author fails, so failed attempts leave orphaned evidence that also locks the stem.

## Findings

- [logic] chupa/author.py:63 AuthorGate.check writes tickets/<stem>/evidence/{replay.json,log.txt,report.json} into checkout.repo before validate_ticket runs. Nothing removes those files if validation, the bug-kind or player-prose checks, or requisition review rejects the candidate. They also stay when the author picks a different stem on retry, or when Author ends in failure_decision. Example: in test_report_author_failure_is_decision, the stem 'broken' passes stem_findings, so its evidence is written; the ticket text 'bad' then fails validation and the run ends as a decision. That leaves an untracked tickets/broken/evidence/ tree in the host checkout. Because `copied` lives only on this gate instance, any later AuthorGate refuses the stem 'broken' as 'already exists'. The working tree is left dirty and the commit's `only=` never picks these files up. (do instead: Copy custody evidence only for the candidate that will actually be committed: after the gate passes and before policy/review, or into a staging path that is cleaned up. Also remove the copied paths on every rejection, stem change, and failure_decision path, and add a test that a rejected or failed report attempt leaves no untracked files under tickets/.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "ccdb1637969afaa04ba7305a193190a9e2f45b52",
  "stem": "report-inbox-triage",
  "reviewed_sha": "ccdb1637969afaa04ba7305a193190a9e2f45b52",
  "summary": "Author copies report evidence into the repo working tree from inside the gate, before validation, and never removes it when an attempt is rejected or Author fails, so failed attempts leave orphaned evidence that also locks the stem.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/author.py",
      "line": 63,
      "message": "AuthorGate.check writes tickets/<stem>/evidence/{replay.json,log.txt,report.json} into checkout.repo before validate_ticket runs. Nothing removes those files if validation, the bug-kind or player-prose checks, or requisition review rejects the candidate. They also stay when the author picks a different stem on retry, or when Author ends in failure_decision. Example: in test_report_author_failure_is_decision, the stem 'broken' passes stem_findings, so its evidence is written; the ticket text 'bad' then fails validation and the run ends as a decision. That leaves an untracked tickets/broken/evidence/ tree in the host checkout. Because `copied` lives only on this gate instance, any later AuthorGate refuses the stem 'broken' as 'already exists'. The working tree is left dirty and the commit's `only=` never picks these files up.",
      "paved_road": "Copy custody evidence only for the candidate that will actually be committed: after the gate passes and before policy/review, or into a staging path that is cleaned up. Also remove the copied paths on every rejection, stem change, and failure_decision path, and add a test that a rejected or failed report attempt leaves no untracked files under tickets/.",
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
