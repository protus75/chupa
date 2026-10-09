# Review: snag

Capture is now drained and written when a consumer raises, but if the child keeps running after the consumer fails, the call blocks until the provider timeout and then raises TimeoutError, so the consumer's exception is lost.

## Findings

- [logic] chupa/seams.py:150 `forward` stores the first callback exception in `consumer_error`, and only the normal-return path re-raises it. If the timeout fires (or the call is cancelled) after the consumer has failed, the `except BaseException` handler kills the group and re-raises TimeoutError/CancelledError, and nothing ever attaches or chains `consumer_error`. A consumer that crashes on an early event of a long-running CLI (the plan-gap-13 watchdog crash) now has its root cause replaced by a TimeoutError at the end of the full provider timeout. The ticket's Definition of rejected forbids swallowing a consumer exception. (do instead: In the timeout/cancel handler, when `consumer_error` is set, keep the kill-and-wait and then surface the consumer error. Either attach `process_capture` and `raise consumer_error from <timeout exc>`, or chain the timeout with `raise ... from consumer_error`. Pick one so the first consumer exception is always visible to the caller.)
- [logic] tests/test_providers.py:778 The test case formerly named `callback` is renamed `callback_timeout`, and its assertion that the consumer's error propagates (`caught.value is error`) is replaced with an expected TimeoutError. The test now enforces the swallowed exception as correct behavior, so it can never catch the loss of the consumer error. (do instead: Have the `callback_timeout` case assert that the consumer's `error` is visible, either as the raised exception or as the `__cause__`/`__context__` of the timeout, whichever form the seams.py fix chooses. Keep the group-kill and no-leaked-task assertions.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "6a61d3346c45601ddea52d7a650b65b5a9c56447",
  "stem": "consumer-error-keeps-capture",
  "reviewed_sha": "6a61d3346c45601ddea52d7a650b65b5a9c56447",
  "summary": "Capture is now drained and written when a consumer raises, but if the child keeps running after the consumer fails, the call blocks until the provider timeout and then raises TimeoutError, so the consumer's exception is lost.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/seams.py",
      "line": 150,
      "message": "`forward` stores the first callback exception in `consumer_error`, and only the normal-return path re-raises it. If the timeout fires (or the call is cancelled) after the consumer has failed, the `except BaseException` handler kills the group and re-raises TimeoutError/CancelledError, and nothing ever attaches or chains `consumer_error`. A consumer that crashes on an early event of a long-running CLI (the plan-gap-13 watchdog crash) now has its root cause replaced by a TimeoutError at the end of the full provider timeout. The ticket's Definition of rejected forbids swallowing a consumer exception.",
      "paved_road": "In the timeout/cancel handler, when `consumer_error` is set, keep the kill-and-wait and then surface the consumer error. Either attach `process_capture` and `raise consumer_error from <timeout exc>`, or chain the timeout with `raise ... from consumer_error`. Pick one so the first consumer exception is always visible to the caller.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/test_providers.py",
      "line": 778,
      "message": "The test case formerly named `callback` is renamed `callback_timeout`, and its assertion that the consumer's error propagates (`caught.value is error`) is replaced with an expected TimeoutError. The test now enforces the swallowed exception as correct behavior, so it can never catch the loss of the consumer error.",
      "paved_road": "Have the `callback_timeout` case assert that the consumer's `error` is visible, either as the raised exception or as the `__cause__`/`__context__` of the timeout, whichever form the seams.py fix chooses. Keep the group-kill and no-leaked-task assertions.",
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
