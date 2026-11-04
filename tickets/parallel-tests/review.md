# Review: snag

The diff meets the structural criteria, but its new readiness gate in the provider kill test adds a second interpreter startup to a fixed 0.15s window, so the timeout variants can fail when every core is busy.

## Findings

- [logic] tests/test_providers.py:834 The scripted child now blocks on `child.stdout.readline()` until the grandchild interpreter has started, and only then prints the `{"type": "tool"}` event. For the `timeout` and `callback_timeout` params, line 843 still sets the provider timeout to 0.15s, and `SubprocessExec.run` starts that timeout at spawn. Two Python interpreter startups must therefore finish within 0.15s of wall-clock time, where the old script needed only one before printing. If they don't, for example when `-n auto` has every core busy, the group is killed before the event arrives, `received` is never set, and `asyncio.wait_for(received.wait(), 5)` at line 859 raises an uncaught TimeoutError that fails the test. This is the load-dependent flake the ticket exists to remove, and it undermines acceptance criterion 2's reliable repeated runs. (do instead: Make the timeout variants independent of how fast the processes start, without lengthening the bound: raise the timeout from the observed event instead of a fixed window measured from spawn. For example, have a test exec wrapper in `tests/` run the real group-kill path under a deadline armed once `received` is set. Keep the wait for grandchild readiness and the `group_exited` check, and do not change `chupa/`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "da74a1abd8996c2b76556e55540aac8928c2e8b8",
  "stem": "parallel-tests",
  "reviewed_sha": "da74a1abd8996c2b76556e55540aac8928c2e8b8",
  "summary": "The diff meets the structural criteria, but its new readiness gate in the provider kill test adds a second interpreter startup to a fixed 0.15s window, so the timeout variants can fail when every core is busy.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/test_providers.py",
      "line": 834,
      "message": "The scripted child now blocks on `child.stdout.readline()` until the grandchild interpreter has started, and only then prints the `{\"type\": \"tool\"}` event. For the `timeout` and `callback_timeout` params, line 843 still sets the provider timeout to 0.15s, and `SubprocessExec.run` starts that timeout at spawn. Two Python interpreter startups must therefore finish within 0.15s of wall-clock time, where the old script needed only one before printing. If they don't, for example when `-n auto` has every core busy, the group is killed before the event arrives, `received` is never set, and `asyncio.wait_for(received.wait(), 5)` at line 859 raises an uncaught TimeoutError that fails the test. This is the load-dependent flake the ticket exists to remove, and it undermines acceptance criterion 2's reliable repeated runs.",
      "paved_road": "Make the timeout variants independent of how fast the processes start, without lengthening the bound: raise the timeout from the observed event instead of a fixed window measured from spawn. For example, have a test exec wrapper in `tests/` run the real group-kill path under a deadline armed once `received` is set. Keep the wait for grandchild readiness and the `group_exited` check, and do not change `chupa/`.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
