# Review: snag

The runtime plan removal and finished-ticket skips are correct, but parse_ticket also stops applying the seed cite law when no plan is passed, which changes validate_ticket/lint behavior on hosts without CHUPA_PLAN.md.

## Findings

- [logic] chupa/tickets.py:401 The ticket's bridge only drops `## Plan contract` resolution and the 'plan is absent' finding when `plan` is None. This line also adds `and plan is not None` to the `source: seed` cite check, which used to run as `_seed_cites(stem, plan_ids, plan or "", path)`. `validate_ticket` passes `read_plan(repo)`, which is None when the host has no CHUPA_PLAN.md. In that case a `source: seed` ticket that is missing its `19.L`/phase-unit cites used to be rejected by validate_ticket and lint, and now it passes. The ticket's Definition of rejected lists any change to validate_ticket or lint behavior. (do instead: Restore `if fm is not None and fm.source == "seed": findings += _seed_cites(stem, plan_ids, plan or "", path)` so that only Plan contract resolution depends on `plan`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3b58f317f7d2d82afba8474aa436f8041c1a2791",
  "stem": "plan-off-serve-path",
  "reviewed_sha": "3b58f317f7d2d82afba8474aa436f8041c1a2791",
  "summary": "The runtime plan removal and finished-ticket skips are correct, but parse_ticket also stops applying the seed cite law when no plan is passed, which changes validate_ticket/lint behavior on hosts without CHUPA_PLAN.md.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/tickets.py",
      "line": 401,
      "message": "The ticket's bridge only drops `## Plan contract` resolution and the 'plan is absent' finding when `plan` is None. This line also adds `and plan is not None` to the `source: seed` cite check, which used to run as `_seed_cites(stem, plan_ids, plan or \"\", path)`. `validate_ticket` passes `read_plan(repo)`, which is None when the host has no CHUPA_PLAN.md. In that case a `source: seed` ticket that is missing its `19.L`/phase-unit cites used to be rejected by validate_ticket and lint, and now it passes. The ticket's Definition of rejected lists any change to validate_ticket or lint behavior.",
      "paved_road": "Restore `if fm is not None and fm.source == \"seed\": findings += _seed_cites(stem, plan_ids, plan or \"\", path)` so that only Plan contract resolution depends on `plan`.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
