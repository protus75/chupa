---
id: declined-box-000395-70ebe69b
kind: declined
link: box-000395-70ebe69b
reopen_after_days: 30
---
A retro over 14 integration runs found that tests/integration/test_host_loop.py::test_host_loop_drives_supervised_fixture_serve takes up to about 21s each time, making it the slowest test in the suite. Its failure-path FixtureLoop is built with a wall clock (datetime.now(UTC)), the real asyncio.sleep, and real timeouts (test_host_loop.py:112). The finding asks for a fake clock and sleep so the test stops waiting in real time.

This only asks to make a test faster. No engine or product behavior is wrong: the test passes, and the report names no incorrect runtime result, no failed run, and no flake. Its own overcorrection risk counts against the change. The test uses real time on purpose so it reaches the real supervised-serve timeout and kill paths, and a fake clock could hide a real hang or an orphaned subprocess. Registry record 000392 declined the same kind of finding about slow daemon-soak integration tests, and record 000394 tombstoned a repeat of it. Reopen if this test's wall time causes real harm: Check or merge timing out, the integration suite going over a configured per-command limit, or tickets failing or parking because of the suite's duration.

- tests/integration/test_host_loop.py:112 builds FixtureLoop with clock=lambda: datetime.now(UTC), sleep=asyncio.sleep, timeout=timeout, so the real-time wait is deliberate
- tests/integration/test_host_loop.py:83 uses the same real clock and sleep with timeout=30
- The message reports test_issue 'slow' only, with null stage and outcome and no failure
- The message's overcorrection_risk says a fake clock could stop the test reaching the real timeout and kill paths
- declined-box-000392-7c3e7668 and tombstone-box-000394-411a2f41 already declined the same kind of request (slow integration tests on the parallel suite's critical path)

Message: box-000395-70ebe69b
