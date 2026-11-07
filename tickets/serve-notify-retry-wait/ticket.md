---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
none

## Context
- tests/test_serve.py
- chupa/notify.py

## Goal / Why
`tests/test_serve.py::test_serve_failed_notify_backoff_and_restart` fails intermittently under a loaded parallel run with `AttributeError: 'NoneType' object has no attribute 'done'` at the wait after `rig.time.advance(NOTIFY_RETRY_S)`. That wait's predicate is `len(deliveries(root)) == 2 and rig.owner.notifications.task.done()`.

The predicate assumes `notifications.task` stays set after the retry delivery finishes. It does not. `_deliver` writes the second delivery, records the new `retry_at` on failure, and returns. The next `Notifications.poll` then sees the task done and clears it to `None` (`chupa/notify.py` `poll`, `task, self.task = self.task, None`), and creates no new task while `retry_at` is in the future. `until` advances the fake clock by `SERVE_POLL_S` every 20 turns, which drives maintenance polls. Under load, the predicate can miss the short gap between "task done" and "next poll", and then dereferences `None`. Observed on 2026-11-07 in 1 of 5 full runs; the test passes alone. The engine's behavior is correct; the test waits on a transient handle.

After this change the wait is on durable state that the failed retry leaves behind, so it no longer depends on event-loop interleaving.

## Scope in / Scope out
- In: in `test_serve_failed_notify_backoff_and_restart`, the wait after `rig.time.advance(NOTIFY_RETRY_S)` becomes `await until(rig, lambda: len(deliveries(root)) == 2 and rig.owner.notifications.retry_at != retry_at)`. `retry_at` is the copy the test already saved before the first `maintenance()` call. `_deliver` assigns a new deadline only when the second send fails, so the predicate holds exactly once the retry has run and failed.
- Out: `chupa/notify.py`, `chupa/serve.py`, `until`, every other assertion in this test, and other tests.

## Scope fence
- tests/test_serve.py

## Acceptance criteria
1. `./dev.py test tests/test_serve.py` exits 0.
2. The wait no longer reads `rig.owner.notifications.task`: `grep -n "notifications.task.done()" tests/test_serve.py` prints nothing. The new predicate would stay false if the retry never ran (deliveries stays 1) or never failed (`retry_at` unchanged), so the test still catches a missing or successful retry.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_serve.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the test retries, sleeps on wall time, or is skipped or marked flaky;
- the predicate can hold without a second delivery and a recorded failed retry;
- `chupa/notify.py`, `chupa/serve.py`, or any file other than `tests/test_serve.py` changes.

## Time budget
- expected: 10m
- stuck: 30m
