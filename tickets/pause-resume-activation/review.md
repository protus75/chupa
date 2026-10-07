# Review: approve

The diff adds `pause`/`resume` CLI routing: with the writer lock held by an engine it publishes an identity-bound request; with no engine it takes the lock and exits 0 with an idle message. It binds one shared pause consumer to the drain's checkpoints, which run before selection and cap accounting. It publishes discovery after the lock, refreshes it after each durable decision and retires it with `b"null\n"` before the lock is released. It migrates only the predecessor's two absence tests to positive evidence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "0f8316b2c800bcab25b1daa7cb62605fcbf1e986",
  "stem": "pause-resume-activation",
  "reviewed_sha": "0f8316b2c800bcab25b1daa7cb62605fcbf1e986",
  "summary": "The diff adds `pause`/`resume` CLI routing: with the writer lock held by an engine it publishes an identity-bound request; with no engine it takes the lock and exits 0 with an idle message. It binds one shared pause consumer to the drain's checkpoints, which run before selection and cap accounting. It publishes discovery after the lock, refreshes it after each durable decision and retires it with `b\"null\\n\"` before the lock is released. It migrates only the predecessor's two absence tests to positive evidence.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
