# Review: snag

The engine, spec, routing and test_diagnose.py changes meet the ticket, but test_harvest.py loosens an existing assertion further than the ticket's named adaptations allow.

## Findings

- [acceptance] tests/test_harvest.py:152 test_drain_reentry_quotes_prior_harvest_and_summarizes_older used to assert `first not in renders[2]`. The diff narrows this to `f"RuntimeError: {first}" not in renders[2]`. That is needed only because the scripted lessons ('Avoid the first dead end.') were written to contain the `first` marker. The changed check no longer proves that attempt 0's raw text is gone from the third render. This weakens an existing assertion beyond the script, surface-filter and adjacency adaptations Scope in allows, which violates AC7 and the 'existing assertion weakened' rejection rule. (do instead: Use lessons that do not contain the `first`/`second` marker strings, for example 'Retry the provider call.', and restore `assert first not in renders[2]` unchanged. Then assert those lesson strings, each prefixed `> `, in renders[1] and renders[2].)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "b0e0fa9e457d357c5246533124e2cae303f85b3c",
  "stem": "spine-diagnosis",
  "reviewed_sha": "b0e0fa9e457d357c5246533124e2cae303f85b3c",
  "summary": "The engine, spec, routing and test_diagnose.py changes meet the ticket, but test_harvest.py loosens an existing assertion further than the ticket's named adaptations allow.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_harvest.py",
      "line": 152,
      "message": "test_drain_reentry_quotes_prior_harvest_and_summarizes_older used to assert `first not in renders[2]`. The diff narrows this to `f\"RuntimeError: {first}\" not in renders[2]`. That is needed only because the scripted lessons ('Avoid the first dead end.') were written to contain the `first` marker. The changed check no longer proves that attempt 0's raw text is gone from the third render. This weakens an existing assertion beyond the script, surface-filter and adjacency adaptations Scope in allows, which violates AC7 and the 'existing assertion weakened' rejection rule.",
      "paved_road": "Use lessons that do not contain the `first`/`second` marker strings, for example 'Retry the provider call.', and restore `assert first not in renders[2]` unchanged. Then assert those lesson strings, each prefixed `> `, in renders[1] and renders[2]."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
