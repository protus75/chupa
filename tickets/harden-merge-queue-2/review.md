# Review: approve

The diff changes only unit 19.P3.merge-queue. It settles the evidence-ownership gap (stages.py owns a new gather_safety_evidence that runs no Verification; gather_evidence reuses it; the seed fences stages.py) and sets all six host-check runner facts. Each matches merged code: child_env with serving=None, ctx.exec_.run, a stuck_minutes timeout, Spool.write redaction, redactor.scrub with OUTPUT_TAIL_CHARS, TimeoutError/ExecutableNotFound mapped to rc null, the Evidence fields, a fail-closed safety designation, and base_red false.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "06ad19fa07689a005bcd8a29d1ba7acd4e4151bb",
  "stem": "harden-merge-queue-2",
  "reviewed_sha": "06ad19fa07689a005bcd8a29d1ba7acd4e4151bb",
  "summary": "The diff changes only unit 19.P3.merge-queue. It settles the evidence-ownership gap (stages.py owns a new gather_safety_evidence that runs no Verification; gather_evidence reuses it; the seed fences stages.py) and sets all six host-check runner facts. Each matches merged code: child_env with serving=None, ctx.exec_.run, a stuck_minutes timeout, Spool.write redaction, redactor.scrub with OUTPUT_TAIL_CHARS, TimeoutError/ExecutableNotFound mapped to rc null, the Evidence fields, a fail-closed safety designation, and base_red false.",
  "findings": [],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
