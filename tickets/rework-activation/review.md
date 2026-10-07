# Review: snag

Rework publication mostly matches the ticket, but a failed or partial commit leaves the reviewed proposal files written and staged in the shared checkout; the next intake would then commit them as human-authored tickets.

## Findings

- [logic] chupa/daemon.py:55 `publish()` writes every proposal into `ctx.repo` and runs `git add` before the commit. If the commit fails, or commits only part of the set (the 'commit' and 'partial' cases in test_production_refuses_failed_rework_publication and test_split_dispatches_reviewed_rework), the outer `except` returns a gate_failed refusal but never restores the working tree. Successor `tickets/<stem>/ticket.md` files, or the edited original, stay on disk and staged. On the next drain, `tickets.intake` treats them as pending hand-authored files and commits them through the human intake path, stamping a machine successor `source: human`, which the ticket explicitly forbids. In the partial case a successor is also already committed with no supersedes map, so it gets dispatched alongside the Reject-queued original. The result is 'state left corrupt on a failure path' and the opposite of 'failed or partial publication writes no map and does not retire the original' with no false success. The refusal tests check only that there is no map and the original stays confirmed. They never check that the checkout is clean or that nothing gets intaken later. (do instead: Make publication all-or-nothing on the ticket plane. On any failure inside or after `publish()`, restore each proposal path to its pre-publication state through `git.py`: unstage it, restore tracked originals from HEAD, delete newly written successor files through the fs seam, and revert a partial commit if one landed, before returning the paved refusal. Extend the commit/partial refusal tests to assert a clean `status_porcelain` and that a following drain intakes no successor.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "64ecc7a194a9fcc8b4c20bcafd0ca1fa4a30fd1f",
  "stem": "rework-activation",
  "reviewed_sha": "64ecc7a194a9fcc8b4c20bcafd0ca1fa4a30fd1f",
  "summary": "Rework publication mostly matches the ticket, but a failed or partial commit leaves the reviewed proposal files written and staged in the shared checkout; the next intake would then commit them as human-authored tickets.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/daemon.py",
      "line": 55,
      "message": "`publish()` writes every proposal into `ctx.repo` and runs `git add` before the commit. If the commit fails, or commits only part of the set (the 'commit' and 'partial' cases in test_production_refuses_failed_rework_publication and test_split_dispatches_reviewed_rework), the outer `except` returns a gate_failed refusal but never restores the working tree. Successor `tickets/<stem>/ticket.md` files, or the edited original, stay on disk and staged. On the next drain, `tickets.intake` treats them as pending hand-authored files and commits them through the human intake path, stamping a machine successor `source: human`, which the ticket explicitly forbids. In the partial case a successor is also already committed with no supersedes map, so it gets dispatched alongside the Reject-queued original. The result is 'state left corrupt on a failure path' and the opposite of 'failed or partial publication writes no map and does not retire the original' with no false success. The refusal tests check only that there is no map and the original stays confirmed. They never check that the checkout is clean or that nothing gets intaken later.",
      "paved_road": "Make publication all-or-nothing on the ticket plane. On any failure inside or after `publish()`, restore each proposal path to its pre-publication state through `git.py`: unstage it, restore tracked originals from HEAD, delete newly written successor files through the fs seam, and revert a partial commit if one landed, before returning the paved refusal. Extend the commit/partial refusal tests to assert a clean `status_porcelain` and that a following drain intakes no successor.",
      "kind": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
