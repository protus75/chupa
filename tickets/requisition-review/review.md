# Review: snag

The code is correct and stays inside the fence, but the new spec's Output format never names the strict `Finding` field keys, so a real model's `snag` or `rma` finding is likely to fail schema validation and come back as a mechanical snag.

## Findings

- [logic] specs/requisition_review.md:50 `RequisitionReply.findings` is `list[Finding]`, and `Finding` is strict with `extra="forbid"` and a required `paved_road`. The Output format only says each finding has `code`, `message`, and "a paved road". It never spells out the `paved_road` key or the optional `path` and `line` keys. A model that writes `paved road`, `road`, or `fix` fails `RequisitionReply.model_validate_json`, so a real buildability snag is swapped for a mechanical `requisition_review` snag and the model's findings are lost. The FakeLLM tests hand-write the exact keys, so they cannot catch this. (do instead: Spell out the exact reply schema in the Output format, as the other specs do. Each finding is an object with `code` (non-blank), `message` (non-blank), `paved_road` (non-blank), and optional `path` (string or null) and `line` (integer >= 1 or null), and no other keys. Reply with only the JSON object.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4df389b51530ccdabc5e6aae2f728335ea847294",
  "stem": "requisition-review",
  "reviewed_sha": "4df389b51530ccdabc5e6aae2f728335ea847294",
  "summary": "The code is correct and stays inside the fence, but the new spec's Output format never names the strict `Finding` field keys, so a real model's `snag` or `rma` finding is likely to fail schema validation and come back as a mechanical snag.",
  "findings": [
    {
      "code": "logic",
      "path": "specs/requisition_review.md",
      "line": 50,
      "message": "`RequisitionReply.findings` is `list[Finding]`, and `Finding` is strict with `extra=\"forbid\"` and a required `paved_road`. The Output format only says each finding has `code`, `message`, and \"a paved road\". It never spells out the `paved_road` key or the optional `path` and `line` keys. A model that writes `paved road`, `road`, or `fix` fails `RequisitionReply.model_validate_json`, so a real buildability snag is swapped for a mechanical `requisition_review` snag and the model's findings are lost. The FakeLLM tests hand-write the exact keys, so they cannot catch this.",
      "paved_road": "Spell out the exact reply schema in the Output format, as the other specs do. Each finding is an object with `code` (non-blank), `message` (non-blank), `paved_road` (non-blank), and optional `path` (string or null) and `line` (integer >= 1 or null), and no other keys. Reply with only the JSON object."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
