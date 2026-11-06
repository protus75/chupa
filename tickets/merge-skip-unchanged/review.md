# Review: approve

Inline merge and the serve queue now both call `merge.main_code_unchanged`, a three-dot `diff_names(reviewed, main)` check that ignores `tickets/`; on a nonempty branch whose main moved only under `tickets/`, they skip the Check reruns, the host checks and the integration tier, while the Merge gates and the queue's safety gates still run; the tests and docs sections 4.5 and 7.2.1 are updated to match.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "640aff57808293594ccae2506d5b69941e2f1327",
  "stem": "merge-skip-unchanged",
  "reviewed_sha": "640aff57808293594ccae2506d5b69941e2f1327",
  "summary": "Inline merge and the serve queue now both call `merge.main_code_unchanged`, a three-dot `diff_names(reviewed, main)` check that ignores `tickets/`; on a nonempty branch whose main moved only under `tickets/`, they skip the Check reruns, the host checks and the integration tier, while the Merge gates and the queue's safety gates still run; the tests and docs sections 4.5 and 7.2.1 are updated to match.",
  "findings": [],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
