# Review: snag

The seed path is mostly correct, but when a re-run of a seeding ticket fails a mechanical gate it overwrites main's checks.json and drops the approvals of seeds already lifted, which can leave the ticket permanently unmergeable.

## Findings

- [logic] chupa/stages.py:752 When a seeding ticket's mechanical Check gates fail, the seed block is skipped and `seeds` stays `[]`. `lift_outbox` still lifts that checks.json to main, which erases the `approve` entries of seeds lifted by an earlier run. On the next run each lifted seed is byte-identical to main, so `_review_seeds` skips it (line 684). It also finds no `prior` entry, so it carries no approval forward and makes no new review call. The merge `SeedSafetyGate` then refuses with 'seed has no approval pinned to its committed blob', and its paved road ('re-run so Check approves the exact committed seed text') can never succeed, so the hold has no reachable release. (do instead: Keep the approvals of already-lifted seeds on every Check write for a seeding ticket. One way: load the prior `seeds` from main's checks.json whenever the ticket is seeding, whether or not the mechanical gates passed. Another: let an own seed that has no prior approval become a candidate again so it is re-reviewed. Add a test with a mechanical Check failure between two runs.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1ef687b844713284ee6c79ec2145b9a396be1912",
  "stem": "requisition-seed-path",
  "reviewed_sha": "1ef687b844713284ee6c79ec2145b9a396be1912",
  "summary": "The seed path is mostly correct, but when a re-run of a seeding ticket fails a mechanical gate it overwrites main's checks.json and drops the approvals of seeds already lifted, which can leave the ticket permanently unmergeable.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 752,
      "message": "When a seeding ticket's mechanical Check gates fail, the seed block is skipped and `seeds` stays `[]`. `lift_outbox` still lifts that checks.json to main, which erases the `approve` entries of seeds lifted by an earlier run. On the next run each lifted seed is byte-identical to main, so `_review_seeds` skips it (line 684). It also finds no `prior` entry, so it carries no approval forward and makes no new review call. The merge `SeedSafetyGate` then refuses with 'seed has no approval pinned to its committed blob', and its paved road ('re-run so Check approves the exact committed seed text') can never succeed, so the hold has no reachable release.",
      "paved_road": "Keep the approvals of already-lifted seeds on every Check write for a seeding ticket. One way: load the prior `seeds` from main's checks.json whenever the ticket is seeding, whether or not the mechanical gates passed. Another: let an own seed that has no prior approval become a candidate again so it is re-reviewed. Add a test with a mechanical Check failure between two runs."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
