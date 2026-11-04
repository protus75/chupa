# Review: snag

The parallel-run changes meet the ticket's mechanical requirements, but they weaken coverage in the only tests of the real subprocess timeout path and in the failed-notify backoff test.

## Findings

- [logic] tests/test_git.py:265 `monkeypatch.setattr(asyncio, "timeout", lambda _: deadline)` discards the `timeout=0.3` argument and fires the deadline by hand, so the test no longer shows that `SubprocessExec.run` honors its `timeout`. If `chupa/seams.py:141` became `asyncio.timeout(None)`, this test would still pass. It also pins the implementation: a seam that enforced the same timeout through another mechanism would never see the manual deadline and would fail at the 60-second `wait_until`. The same patch in `tests/test_providers.py:850` drops `timeout=0.15` in the same way, and a search of `tests/` found no other test where the real seam's timeout expires. (do instead: Have the patched factory record the value it receives and assert it equals the configured timeout (0.3 here, 0.15 in `test_providers.py`). Better, drive the timeout without replacing `asyncio.timeout`, so the test checks behavior and not the mechanism.)
- [logic] tests/test_serve.py:1589 The backoff check used to call `await rig.owner.maintenance()` on each of 100 steps, which forced a poll after the unrelated journal append. It now only waits for the fake clock to advance 10 seconds, which `until` does after about 2,000 spins, and nothing requires a maintenance or notification poll to finish in that window. `until` advances the clock on loop iterations rather than on completed passes, so on a loaded machine the run loop may not reach `notifications.poll()` before the window closes. A regression that resets `retry_at` on journal arrival would then still pass `len(intents()) == len(deliveries(root)) == 1`. This is an iteration-count dependence of the kind the ticket removes, and it makes the assertion vacuous under load. (do instead: After the journal append, wait for a real completed boundary before asserting, such as a counted wrapper around `notifications.poll` that has run after the append while the fake clock stays inside the retry window. `test_report_consumer_is_sequential` uses a similar approach with its heartbeat-change wait.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "d4e9cc002ea22383a6c1d604cd283e361b528f94",
  "stem": "parallel-tests",
  "reviewed_sha": "d4e9cc002ea22383a6c1d604cd283e361b528f94",
  "summary": "The parallel-run changes meet the ticket's mechanical requirements, but they weaken coverage in the only tests of the real subprocess timeout path and in the failed-notify backoff test.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/test_git.py",
      "line": 265,
      "message": "`monkeypatch.setattr(asyncio, \"timeout\", lambda _: deadline)` discards the `timeout=0.3` argument and fires the deadline by hand, so the test no longer shows that `SubprocessExec.run` honors its `timeout`. If `chupa/seams.py:141` became `asyncio.timeout(None)`, this test would still pass. It also pins the implementation: a seam that enforced the same timeout through another mechanism would never see the manual deadline and would fail at the 60-second `wait_until`. The same patch in `tests/test_providers.py:850` drops `timeout=0.15` in the same way, and a search of `tests/` found no other test where the real seam's timeout expires.",
      "paved_road": "Have the patched factory record the value it receives and assert it equals the configured timeout (0.3 here, 0.15 in `test_providers.py`). Better, drive the timeout without replacing `asyncio.timeout`, so the test checks behavior and not the mechanism.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/test_serve.py",
      "line": 1589,
      "message": "The backoff check used to call `await rig.owner.maintenance()` on each of 100 steps, which forced a poll after the unrelated journal append. It now only waits for the fake clock to advance 10 seconds, which `until` does after about 2,000 spins, and nothing requires a maintenance or notification poll to finish in that window. `until` advances the clock on loop iterations rather than on completed passes, so on a loaded machine the run loop may not reach `notifications.poll()` before the window closes. A regression that resets `retry_at` on journal arrival would then still pass `len(intents()) == len(deliveries(root)) == 1`. This is an iteration-count dependence of the kind the ticket removes, and it makes the assertion vacuous under load.",
      "paved_road": "After the journal append, wait for a real completed boundary before asserting, such as a counted wrapper around `notifications.poll` that has run after the append while the fake clock stays inside the retry window. `test_report_consumer_is_sequential` uses a similar approach with its heartbeat-change wait.",
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
