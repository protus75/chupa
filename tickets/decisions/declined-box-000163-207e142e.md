---
id: declined-box-000163-207e142e
kind: declined
link: box-000163-207e142e
reopen_after_days: 90
---
When a test's FakeLLM runs out of scripted replies it raises AssertionError. `Driver.run` catches that error with its generic `except Exception` and ends the run `infra_error`. A test that forgets to script a call, such as the diagnosis call after a non-ok terminal, can therefore pass on that fail-closed path instead of failing. The proposal is a dedicated exhaustion exception type that the driver re-raises.

The swallowing is real. But FakeLLM only exists in tests, and production providers never raise its exhaustion error, so no runtime behavior is wrong. This is a test-only improvement. No test has been shown to pass for the wrong reason because of it. The admission bar declines test-only improvements unless they are tied to reachable incorrect runtime behavior. Reopen if a merged test is found passing only because an unscripted FakeLLM call was turned into `infra_error`, for example a diagnosis or review path whose assertion holds by accident.

- chupa/llm.py:72 FakeLLM raises AssertionError('FakeLLM script exhausted ...') when its script is empty
- chupa/driver.py:352-353 and :375-376 catch every Exception from the LLM call or review and pass it to `failed`, which ends the run `done('infra_error')`
- tests/integration/test_driver.py:357-359 checks the exhaustion error only on a direct FakeLLM call, not through the driver
- FakeLLM is a test double; production ProviderLLM never raises this error, so runtime behavior is unchanged

Message: box-000163-207e142e
