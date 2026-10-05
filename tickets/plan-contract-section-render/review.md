# Review: approve

The resolver now takes only canonical ids and rejects anything else. `validate_ticket` runs `plan_id` on each bullet before it calls the resolver. The resolver tests change only their input form. The new stage tests cover two cases: a ticket citing `section 11` renders that section in the Implement prompt, and a bare `11` bullet is refused at intake. Every file touched is inside the fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "92310b6a79d9658986695cf5954df52c6998f58b",
  "stem": "plan-contract-section-render",
  "reviewed_sha": "92310b6a79d9658986695cf5954df52c6998f58b",
  "summary": "The resolver now takes only canonical ids and rejects anything else. `validate_ticket` runs `plan_id` on each bullet before it calls the resolver. The resolver tests change only their input form. The new stage tests cover two cases: a ticket citing `section 11` renders that section in the Implement prompt, and a bare `11` bullet is refused at intake. Every file touched is inside the fence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
