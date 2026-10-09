# Review: snag

The drain-and-capture path works, but the exceptional branch turns an outer asyncio cancellation into the consumer's RuntimeError, so cancellation is swallowed and cancel/kill behavior changes.

## Findings

- [logic] chupa/seams.py:160 If a consumer error is pending, `except BaseException as exc: ... raise consumer_error from exc` replaces every unwind with the consumer's exception. That includes `asyncio.CancelledError` from outer cancellation, so the cancellation is suppressed. It breaks asyncio's contract: the task's cancelling() count is never consumed, and an enclosing asyncio.timeout/TaskGroup will not see the cancellation. It also changes how the engine's own kill paths behave. In `driver._kill`, `race.call.cancel()` followed by `cleanup()` (and likewise in `abort()`) ignores only CancelledError/LLMAborted. Now the call result is a RuntimeError, so a deliberate stage kill or abort after a consumer error is re-raised as a cleanup failure. The ticket's definition of rejected forbids this kind of unwind-behavior change. The edited `test_event_callback_unwind_kills_group[callback_cancel]` case pins the swallowing by expecting RuntimeError from `task.cancel()`. (do instead: In the exceptional branch, attach `process_capture` to `consumer_error` if you want to keep it there, but re-raise the original `exc` for CancelledError. Re-raising it for TimeoutError too keeps timeout behavior unchanged. Use `raise consumer_error` only on the normal EOF path (line 166). Update the `callback_cancel` (and `callback_timeout`) test cases to expect the original CancelledError/TimeoutError.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "8c47bfe7ed5a946e638e28b5f20c6b90c5bb660c",
  "stem": "consumer-error-keeps-capture",
  "reviewed_sha": "8c47bfe7ed5a946e638e28b5f20c6b90c5bb660c",
  "summary": "The drain-and-capture path works, but the exceptional branch turns an outer asyncio cancellation into the consumer's RuntimeError, so cancellation is swallowed and cancel/kill behavior changes.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/seams.py",
      "line": 160,
      "message": "If a consumer error is pending, `except BaseException as exc: ... raise consumer_error from exc` replaces every unwind with the consumer's exception. That includes `asyncio.CancelledError` from outer cancellation, so the cancellation is suppressed. It breaks asyncio's contract: the task's cancelling() count is never consumed, and an enclosing asyncio.timeout/TaskGroup will not see the cancellation. It also changes how the engine's own kill paths behave. In `driver._kill`, `race.call.cancel()` followed by `cleanup()` (and likewise in `abort()`) ignores only CancelledError/LLMAborted. Now the call result is a RuntimeError, so a deliberate stage kill or abort after a consumer error is re-raised as a cleanup failure. The ticket's definition of rejected forbids this kind of unwind-behavior change. The edited `test_event_callback_unwind_kills_group[callback_cancel]` case pins the swallowing by expecting RuntimeError from `task.cancel()`.",
      "paved_road": "In the exceptional branch, attach `process_capture` to `consumer_error` if you want to keep it there, but re-raise the original `exc` for CancelledError. Re-raising it for TimeoutError too keeps timeout behavior unchanged. Use `raise consumer_error` only on the normal EOF path (line 166). Update the `callback_cancel` (and `callback_timeout`) test cases to expect the original CancelledError/TimeoutError.",
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
