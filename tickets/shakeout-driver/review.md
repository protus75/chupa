# Review: snag

The invalid_output_exhausted member never checks its main observable: the bounded re-prompt count and the re-prompt finding text are asserted inside a FakeLLM callable, and the driver swallows that assertion, so the member is green whether or not those checks hold.

## Findings

- [logic] eval/shakeout/driver.py:101 The checks for exactly `retry + 1` implement requests and for `[invalid_artifact]` in each re-prompt sit inside the `diagnosis` script callable. FakeLLM.call appends the request before it runs the callable, and the diagnose request also has `ticket == stem`. So `requests` always holds allowance + 1 entries, and `assert len(requests) == allowance` always fails. That AssertionError is raised inside `llm_call`. Driver.run catches it as `except Exception` -> `infra_error`, and diagnose() turns that into a mechanical `abandon-human`, which dispatches to the reject queue just as `reject` would. The member's outer asserts (terminal, harvest finding code, next ticket merged) still pass, so the member is green. Its central observable (a bounded allowance of implement calls, each re-prompt rendering the prior validation error) can never fail. The scripted `reject` diagnosis is also never used. (do instead: Move the checks out of the callable and run them after `await bench.drain()`. Filter `bench.llm.requests` to `ticket == stem and surface == 'implement'`, assert the count equals `bench.config.caps.retry + 1`, and assert every re-prompt after the first contains the `[invalid_artifact]` finding line. Script the diagnosis as a plain string reply. Also assert the diagnosis signal is not mechanical, so a swallowed exception can no longer hide.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "40a74be24a34855dab7639d24e15596b7c231940",
  "stem": "shakeout-driver",
  "reviewed_sha": "40a74be24a34855dab7639d24e15596b7c231940",
  "summary": "The invalid_output_exhausted member never checks its main observable: the bounded re-prompt count and the re-prompt finding text are asserted inside a FakeLLM callable, and the driver swallows that assertion, so the member is green whether or not those checks hold.",
  "findings": [
    {
      "code": "logic",
      "path": "eval/shakeout/driver.py",
      "line": 101,
      "message": "The checks for exactly `retry + 1` implement requests and for `[invalid_artifact]` in each re-prompt sit inside the `diagnosis` script callable. FakeLLM.call appends the request before it runs the callable, and the diagnose request also has `ticket == stem`. So `requests` always holds allowance + 1 entries, and `assert len(requests) == allowance` always fails. That AssertionError is raised inside `llm_call`. Driver.run catches it as `except Exception` -> `infra_error`, and diagnose() turns that into a mechanical `abandon-human`, which dispatches to the reject queue just as `reject` would. The member's outer asserts (terminal, harvest finding code, next ticket merged) still pass, so the member is green. Its central observable (a bounded allowance of implement calls, each re-prompt rendering the prior validation error) can never fail. The scripted `reject` diagnosis is also never used.",
      "paved_road": "Move the checks out of the callable and run them after `await bench.drain()`. Filter `bench.llm.requests` to `ticket == stem and surface == 'implement'`, assert the count equals `bench.config.caps.retry + 1`, and assert every re-prompt after the first contains the `[invalid_artifact]` finding line. Script the diagnosis as a plain string reply. Also assert the diagnosis signal is not mechanical, so a swallowed exception can no longer hide."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
