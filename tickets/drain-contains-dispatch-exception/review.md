# Review: approve

The handler in `_Drain._run_one` contains an exception only when it is the dispatch task's own and the drain is not stopping, journals one `infra_error` that names the exception type, and re-raises control-monitor, kill-path and cancellation failures; the new and updated tests cover every required branch, the Reject-queue release, and the probes that now expect a contained error.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "df3f42475ba03b268fc41a480acbebbac625fa52",
  "stem": "drain-contains-dispatch-exception",
  "reviewed_sha": "df3f42475ba03b268fc41a480acbebbac625fa52",
  "summary": "The handler in `_Drain._run_one` contains an exception only when it is the dispatch task's own and the drain is not stopping, journals one `infra_error` that names the exception type, and re-raises control-monitor, kill-path and cancellation failures; the new and updated tests cover every required branch, the Reject-queue release, and the probes that now expect a contained error.",
  "findings": [],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
