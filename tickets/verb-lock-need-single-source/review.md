# Review: snag

The diff meets the ticket in production code and docs, but the unit test for the engine-verb decision checks a copy of the expression instead of the production code path.

## Findings

- [acceptance] tests/unit/test_lock_holder.py:16 Criterion 6's first bullet asks for a test showing the engine-verb decision is true for `drain`/`serve` and false for `triage`, `eval` and a missing `verb` key. `test_engine_verbs` never calls production code. It re-evaluates its own copy, `holder.get("verb") in ENGINE_VERBS`, so it only pins which verbs the constant contains. The real decision in `_require_engine` (`(exc.holder or {}).get("verb") or "unknown holder"`, then the membership test) is never run for `drain`, `eval`, a missing key or a `None` holder. A regression there, such as a changed fallback or an inverted check, would not fail this test. (do instead: Drive the real path for each case. Extend `test_request_routing` (or a new parametrized test) so the holder covers `drain`, `serve`, `triage`, `eval`, a dict without `verb`, and `None`, each raising `LockHeld` from the fake `Lockfile.acquire`. Assert that `_control`/`_verdict`/`_retro` publish exactly one request for `drain` and `serve`, and raise `runner.Refusal` and publish nothing for the other cases. Then delete the copied-expression test.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3e9e0161cca841e222938404775c6d2471ca18c7",
  "stem": "verb-lock-need-single-source",
  "reviewed_sha": "3e9e0161cca841e222938404775c6d2471ca18c7",
  "summary": "The diff meets the ticket in production code and docs, but the unit test for the engine-verb decision checks a copy of the expression instead of the production code path.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/unit/test_lock_holder.py",
      "line": 16,
      "message": "Criterion 6's first bullet asks for a test showing the engine-verb decision is true for `drain`/`serve` and false for `triage`, `eval` and a missing `verb` key. `test_engine_verbs` never calls production code. It re-evaluates its own copy, `holder.get(\"verb\") in ENGINE_VERBS`, so it only pins which verbs the constant contains. The real decision in `_require_engine` (`(exc.holder or {}).get(\"verb\") or \"unknown holder\"`, then the membership test) is never run for `drain`, `eval`, a missing key or a `None` holder. A regression there, such as a changed fallback or an inverted check, would not fail this test.",
      "paved_road": "Drive the real path for each case. Extend `test_request_routing` (or a new parametrized test) so the holder covers `drain`, `serve`, `triage`, `eval`, a dict without `verb`, and `None`, each raising `LockHeld` from the fake `Lockfile.acquire`. Assert that `_control`/`_verdict`/`_retro` publish exactly one request for `drain` and `serve`, and raise `runner.Refusal` and publish nothing for the other cases. Then delete the copied-expression test.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
