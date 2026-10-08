# Review: approve

The diff binds spec-gap Reject arrivals to their plan units. It skips auto-keep while the units are unchanged and releases with a machine keep plus one retry draw once the committed unit bytes change. Plan-bound terminals are no longer premise-parked, retired hardeners are excluded from dispatch, the parked line names the unit and the fix-then-drain road, and confirm allows a second keep after a bound unit changes, each with a test that can fail.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4373467ddc0334858a91c54e844ac3eab821707d",
  "stem": "plan-bound-reject-release",
  "reviewed_sha": "4373467ddc0334858a91c54e844ac3eab821707d",
  "summary": "The diff binds spec-gap Reject arrivals to their plan units. It skips auto-keep while the units are unchanged and releases with a machine keep plus one retry draw once the committed unit bytes change. Plan-bound terminals are no longer premise-parked, retired hardeners are excluded from dispatch, the parked line names the unit and the fix-then-drain road, and confirm allows a second keep after a bound unit changes, each with a test that can fail.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
