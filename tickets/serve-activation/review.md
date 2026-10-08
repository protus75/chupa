# Review: snag

The serve lifetime is mostly wired as the unit requires, but its own shutdown cancellations each fire the ordinary worker-failure callback, and the governing test cannot detect this because it only asserts that the list of failures is non-empty.

## Findings

- [logic] chupa/serve.py:341 WorkerFailureObserver is given `projection=lambda: self.control.projection`, while non-kill stops go through `self.stopper.stop(replace(..., kill_requested=True))`. A non-kill stop is a worker failure, unexpected return, SIGINT/SIGTERM or outer cancellation. In each case DaemonTasks.run (via _stop_workers) and WorkerStop cancel the sibling workers, while the observer reads the real projection, where kill_requested is False. So every cancelled sibling raises CancelledError into `self.failure`. One scripted consumer ValueError produces 4 callbacks: the ValueError plus 3 CancelledErrors. An orderly signal stop logs 4 spurious `worker_failure` events. 19.P3.serve-activation requires exactly 'one ordinary callback without matching kill' and says an orderly signal stop uses the same cleanup ownership. Reporting the lifetime's own cleanup cancellations as worker failures is wrong behavior. (do instead: Deliver only the first ordinary worker failure to the failure callback. Do not report cancellations that serve's own stop/cleanup causes. For example, latch a memory-only stopping flag that the observer's projection, or a wrapped failure callback, consults before notifying. Keep WorkerFailureObserver's predecessor contract and the post-kill suppression unchanged.)
- [logic] tests/test_serve.py:292 test_serve_worker_failure_and_kill_suppression asserts only `await run == 1 and failures`. It cannot fail when spurious shutdown callbacks are delivered, so it does not pin the 'one ordinary callback without matching kill' obligation. It also does not cover suppressed shutdown callbacks after a matching kill within this test. (do instead: For each ending, assert exactly one failure callback carrying the scripted consumer error (or the unexpected-return/cancellation error). Add a matching-kill case that asserts no callbacks. The assertions must fail against the current multi-callback behavior.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "ff92996a5ba66eba19288bfb2a9c5c66db143e5f",
  "stem": "serve-activation",
  "reviewed_sha": "ff92996a5ba66eba19288bfb2a9c5c66db143e5f",
  "summary": "The serve lifetime is mostly wired as the unit requires, but its own shutdown cancellations each fire the ordinary worker-failure callback, and the governing test cannot detect this because it only asserts that the list of failures is non-empty.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 341,
      "message": "WorkerFailureObserver is given `projection=lambda: self.control.projection`, while non-kill stops go through `self.stopper.stop(replace(..., kill_requested=True))`. A non-kill stop is a worker failure, unexpected return, SIGINT/SIGTERM or outer cancellation. In each case DaemonTasks.run (via _stop_workers) and WorkerStop cancel the sibling workers, while the observer reads the real projection, where kill_requested is False. So every cancelled sibling raises CancelledError into `self.failure`. One scripted consumer ValueError produces 4 callbacks: the ValueError plus 3 CancelledErrors. An orderly signal stop logs 4 spurious `worker_failure` events. 19.P3.serve-activation requires exactly 'one ordinary callback without matching kill' and says an orderly signal stop uses the same cleanup ownership. Reporting the lifetime's own cleanup cancellations as worker failures is wrong behavior.",
      "paved_road": "Deliver only the first ordinary worker failure to the failure callback. Do not report cancellations that serve's own stop/cleanup causes. For example, latch a memory-only stopping flag that the observer's projection, or a wrapped failure callback, consults before notifying. Keep WorkerFailureObserver's predecessor contract and the post-kill suppression unchanged.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/test_serve.py",
      "line": 292,
      "message": "test_serve_worker_failure_and_kill_suppression asserts only `await run == 1 and failures`. It cannot fail when spurious shutdown callbacks are delivered, so it does not pin the 'one ordinary callback without matching kill' obligation. It also does not cover suppressed shutdown callbacks after a matching kill within this test.",
      "paved_road": "For each ending, assert exactly one failure callback carrying the scripted consumer error (or the unexpected-return/cancellation error). Add a matching-kill case that asserts no callbacks. The assertions must fail against the current multi-callback behavior.",
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
