# Review: snag

The diff meets the GO-grade report, budget and registration criteria, but it also removes the provider preflight from both eval entry points, which the ticket did not ask for.

## Findings

- [scope] eval/harness.py:481 The diff deletes the existing `llm.preflight()` refusal from `_run` and the `probe.preflight()` refusal from `author_fixtures`. It replaces them with a comment saying eval spends only on bounded measured calls. No acceptance criterion or Scope-in item asks for this, and the plan unit says to preserve the existing harness behaviour and seams. With the change, a missing CLI, an expired login or an unroutable model is no longer refused before the run. Each fixture instead records a failure outcome, and the run still journals a NO_GO signal and writes a report that looks like measured evidence. The tests that motivated the removal monkeypatch `ProviderLLM` with a `FakeLLM` that has no `preflight`, so the removal works around a test double rather than meeting a requirement. (do instead: Restore both preflight refusals unchanged. In the tests that monkeypatch `ProviderLLM`, give the fake an async `preflight()` that returns `[]`. If preflight probes really do spend unbounded money, file that as a separate Suggestion Box item.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "7f1832f7576d2f583215bf225651bb784d19e5eb",
  "stem": "go-grade-machinery",
  "reviewed_sha": "7f1832f7576d2f583215bf225651bb784d19e5eb",
  "summary": "The diff meets the GO-grade report, budget and registration criteria, but it also removes the provider preflight from both eval entry points, which the ticket did not ask for.",
  "findings": [
    {
      "code": "scope",
      "path": "eval/harness.py",
      "line": 481,
      "message": "The diff deletes the existing `llm.preflight()` refusal from `_run` and the `probe.preflight()` refusal from `author_fixtures`. It replaces them with a comment saying eval spends only on bounded measured calls. No acceptance criterion or Scope-in item asks for this, and the plan unit says to preserve the existing harness behaviour and seams. With the change, a missing CLI, an expired login or an unroutable model is no longer refused before the run. Each fixture instead records a failure outcome, and the run still journals a NO_GO signal and writes a report that looks like measured evidence. The tests that motivated the removal monkeypatch `ProviderLLM` with a `FakeLLM` that has no `preflight`, so the removal works around a test double rather than meeting a requirement.",
      "paved_road": "Restore both preflight refusals unchanged. In the tests that monkeypatch `ProviderLLM`, give the fake an async `preflight()` that returns `[]`. If preflight probes really do spend unbounded money, file that as a separate Suggestion Box item.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
