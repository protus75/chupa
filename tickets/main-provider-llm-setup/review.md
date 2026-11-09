# Review: approve

The diff moves the duplicated build-and-preflight sequence for triage and review into one helper, `_preflighted_llm(checkout, session)`, which reads every argument from the checkout. Both call sites stay inside their existing try/finally blocks, and each path gets a preflight-failure test that checks exit 2, the stderr message, no journaled verdict (review only) and that the lock was released.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "59c4e5b53752d8417ebd306aa5e499d924b41a88",
  "stem": "main-provider-llm-setup",
  "reviewed_sha": "59c4e5b53752d8417ebd306aa5e499d924b41a88",
  "summary": "The diff moves the duplicated build-and-preflight sequence for triage and review into one helper, `_preflighted_llm(checkout, session)`, which reads every argument from the checkout. Both call sites stay inside their existing try/finally blocks, and each path gets a preflight-failure test that checks exit 2, the stderr message, no journaled verdict (review only) and that the lock was released.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
