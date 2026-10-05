# Review: approve

The diff meets every acceptance criterion and stays inside the scope fence. On a non-ok terminal it harvests, takes the infra draw, journals the terminal, then removes the worktree and prunes, in that order. The harvest is a closed allowlist (prompts excluded, so the diff does not leak through the stage log), it commits through `lift_outbox` (narrowed by `only`), and the prior and older attempts render inside the existing `prior_attempts` block with each payload line quoted.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "bc8611dc272e033158c10a535124c04b05e0a29f",
  "stem": "spine-harvest",
  "reviewed_sha": "bc8611dc272e033158c10a535124c04b05e0a29f",
  "summary": "The diff meets every acceptance criterion and stays inside the scope fence. On a non-ok terminal it harvests, takes the infra draw, journals the terminal, then removes the worktree and prunes, in that order. The harvest is a closed allowlist (prompts excluded, so the diff does not leak through the stage log), it commits through `lift_outbox` (narrowed by `only`), and the prior and older attempts render inside the existing `prior_attempts` block with each payload line quoted.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
