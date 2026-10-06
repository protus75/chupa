# Review: approve

The new test runs the production `drain` through the real `drive` pipeline with only the LLM replies faked: the predecessor seeds a successor that depends on it, the seed is reviewed and lifted in one `chupa(<stem>): seeds` commit, the drain re-scans after the merge, and the successor is dispatched in the same invocation; the test checks the commit count, the `ticket_intake` provenance with its seed commit and blob, and that the predecessor's merge comes before the successor's `running`, all inside the fence. I read this from the code but could not run it here because the sandbox blocked the test commands; the branch's checks commit is the only sign that it passes.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "563325515f1835058018017915539d0600e9c571",
  "stem": "seed-successor-proof",
  "reviewed_sha": "563325515f1835058018017915539d0600e9c571",
  "summary": "The new test runs the production `drain` through the real `drive` pipeline with only the LLM replies faked: the predecessor seeds a successor that depends on it, the seed is reviewed and lifted in one `chupa(<stem>): seeds` commit, the drain re-scans after the merge, and the successor is dispatched in the same invocation; the test checks the commit count, the `ticket_intake` provenance with its seed commit and blob, and that the predecessor's merge comes before the successor's `running`, all inside the fence. I read this from the code but could not run it here because the sandbox blocked the test commands; the branch's checks commit is the only sign that it passes.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
