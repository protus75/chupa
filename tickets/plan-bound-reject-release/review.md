# Review: snag

The plan-bound hold and release logic matches the ticket, but `_scan` now reads the plan from HEAD on every drain whenever a working-tree CHUPA_PLAN.md exists, so the drain crashes when that file is not committed.

## Findings

- [logic] chupa/drain.py:301 `committed_plan` runs `git show HEAD:CHUPA_PLAN.md` whenever `plan is not None`, even when no plan-bound arrival exists. If CHUPA_PLAN.md is in the working tree but not in HEAD (untracked, only staged, or deleted from HEAD), `Git._run` raises GitError. That aborts every drain scan, including drains that have nothing to do with a plan-bound arrival. The merge base read only the working-tree file and tolerated this state. (do instead: Read the committed plan only when `plan_bound` is true, and treat a missing `HEAD:CHUPA_PLAN.md` as an empty plan (every unit `absent`) instead of letting GitError escape `_scan`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0cfe3556ea209b2a12b23586b39fd6d573e17e9d",
  "stem": "plan-bound-reject-release",
  "reviewed_sha": "0cfe3556ea209b2a12b23586b39fd6d573e17e9d",
  "summary": "The plan-bound hold and release logic matches the ticket, but `_scan` now reads the plan from HEAD on every drain whenever a working-tree CHUPA_PLAN.md exists, so the drain crashes when that file is not committed.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/drain.py",
      "line": 301,
      "message": "`committed_plan` runs `git show HEAD:CHUPA_PLAN.md` whenever `plan is not None`, even when no plan-bound arrival exists. If CHUPA_PLAN.md is in the working tree but not in HEAD (untracked, only staged, or deleted from HEAD), `Git._run` raises GitError. That aborts every drain scan, including drains that have nothing to do with a plan-bound arrival. The merge base read only the working-tree file and tolerated this state.",
      "paved_road": "Read the committed plan only when `plan_bound` is true, and treat a missing `HEAD:CHUPA_PLAN.md` as an empty plan (every unit `absent`) instead of letting GitError escape `_scan`.",
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
