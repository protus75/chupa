# Review: approve

Both preflight version children now get child_env(self._env, self._config) with no serving provider, so they receive no provider key while PATH and HOME are kept; probes are untouched, and the new test asserts this for all four version calls and would fail on the merge base.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5c11c18f7a3dfdd0f70c0f9c4cbd31fcb9405f17",
  "stem": "preflight-child-env",
  "reviewed_sha": "5c11c18f7a3dfdd0f70c0f9c4cbd31fcb9405f17",
  "summary": "Both preflight version children now get child_env(self._env, self._config) with no serving provider, so they receive no provider key while PATH and HOME are kept; probes are untouched, and the new test asserts this for all four version calls and would fail on the merge base.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
