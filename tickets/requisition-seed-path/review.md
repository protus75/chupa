# Review: snag

The seed lift and the merge re-check are wired correctly, but each seed is reviewed at the seeding ticket's agent_tier instead of the seed's own agent_tier, as the ticket requires.

## Findings

- [acceptance] chupa/stages.py:700 `_review_seeds` calls `review_ticket(..., tier=ticket.frontmatter.agent_tier, ...)`, which is the SEEDING ticket's tier. Scope in says each seed is judged 'at the SEED's `agent_tier`'. A seed authored `agent_tier: high` under a `medium` seeding ticket is reviewed on the wrong tier and route. The tests miss this because the fixture seeds and the seeding ticket both default to `medium`. (do instead: Pass `tier=parsed.frontmatter.agent_tier`, the seed's validated frontmatter. Add a seed-path case where the seed's tier differs from the seeding ticket's, with a route for that tier, and assert that the requisition request carries the seed's tier.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "720abebdd4c2b243760c0333a9f48668b838c9b1",
  "stem": "requisition-seed-path",
  "reviewed_sha": "720abebdd4c2b243760c0333a9f48668b838c9b1",
  "summary": "The seed lift and the merge re-check are wired correctly, but each seed is reviewed at the seeding ticket's agent_tier instead of the seed's own agent_tier, as the ticket requires.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/stages.py",
      "line": 700,
      "message": "`_review_seeds` calls `review_ticket(..., tier=ticket.frontmatter.agent_tier, ...)`, which is the SEEDING ticket's tier. Scope in says each seed is judged 'at the SEED's `agent_tier`'. A seed authored `agent_tier: high` under a `medium` seeding ticket is reviewed on the wrong tier and route. The tests miss this because the fixture seeds and the seeding ticket both default to `medium`.",
      "paved_road": "Pass `tier=parsed.frontmatter.agent_tier`, the seed's validated frontmatter. Add a seed-path case where the seed's tier differs from the seeding ticket's, with a route for that tier, and assert that the requisition request carries the seed's tier."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
