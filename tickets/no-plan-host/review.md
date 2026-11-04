# Review: snag

Seed review still crashes on a host with no plan: `_review_seeds` passes the `None` from `read_plan` to `_review_one`, which requires a plan string.

## Findings

- [logic] chupa/stages.py:1129 `plan = read_plan(ctx.repo)` yields `None` when `CHUPA_PLAN.md` is absent, and `_review_seeds` passes it unchanged to `_review_one` (declared `plan: str`). `_review_one` then calls `required_units(plan, seed_stem, citations)`, which reaches `registry_rows` and `_REGISTRY.findall(None)` and raises `TypeError`. `resolve_plan_contract(plan, ...)` on the same path would also fail, on `plan.splitlines`. So any ticket with `tickets` in its scope fence that adds a seed candidate on a no-plan host still crashes at seed review. The diff only replaces the `FileNotFoundError` with a `TypeError`. The ticket names `stages.py` seed review as in scope and its Definition of rejected covers any path that can still raise because the plan is absent. No test covers this path. (do instead: Make the seed-review path tolerate an absent plan the way `implement_stage` and `hold_on_hardening` do: use `plan = read_plan(ctx.repo) or ""` at this line, so `required_units` returns no units and citations fall through to `validate_ticket`, which reports a `## Plan contract` citation against an absent plan as a ticket finding. Add a no-plan seed-review test to `tests/test_no_plan_host.py` that fails on the current code.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3f9a1f5c43bf0f10bb996588e91653a93b7ea314",
  "stem": "no-plan-host",
  "reviewed_sha": "3f9a1f5c43bf0f10bb996588e91653a93b7ea314",
  "summary": "Seed review still crashes on a host with no plan: `_review_seeds` passes the `None` from `read_plan` to `_review_one`, which requires a plan string.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 1129,
      "message": "`plan = read_plan(ctx.repo)` yields `None` when `CHUPA_PLAN.md` is absent, and `_review_seeds` passes it unchanged to `_review_one` (declared `plan: str`). `_review_one` then calls `required_units(plan, seed_stem, citations)`, which reaches `registry_rows` and `_REGISTRY.findall(None)` and raises `TypeError`. `resolve_plan_contract(plan, ...)` on the same path would also fail, on `plan.splitlines`. So any ticket with `tickets` in its scope fence that adds a seed candidate on a no-plan host still crashes at seed review. The diff only replaces the `FileNotFoundError` with a `TypeError`. The ticket names `stages.py` seed review as in scope and its Definition of rejected covers any path that can still raise because the plan is absent. No test covers this path.",
      "paved_road": "Make the seed-review path tolerate an absent plan the way `implement_stage` and `hold_on_hardening` do: use `plan = read_plan(ctx.repo) or \"\"` at this line, so `required_units` returns no units and citations fall through to `validate_ticket`, which reports a `## Plan contract` citation against an absent plan as a ticket finding. Add a no-plan seed-review test to `tests/test_no_plan_host.py` that fails on the current code.",
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
