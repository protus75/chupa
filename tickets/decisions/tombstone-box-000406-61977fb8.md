---
id: tombstone-box-000406-61977fb8
kind: tombstone
link: declined-box-000392-7c3e7668
reopen_after_days: 30
---
A retro over 9 integration runs found that a few daemon-soak tests in tests/integration/test_daemon_soak_runner.py (17-23s each) and test_host_loop_drives_supervised_fixture_serve in tests/integration/test_host_loop.py (27.5s) take most of the integration suite's time. It proposes running one shared soak for the tests that only read its evidence, faking the clock and sleeps, and shrinking the member fixtures.

This repeats requests the registry has already decided. Record declined-box-000392-7c3e7668 declined speeding up the daemon-soak integration tests that set the suite's critical path. Record tombstone-box-000394-411a2f41 already pointed a second report about test_daemon_soak_is_rederivable to that record. Record declined-box-000395-70ebe69b declined faking the clock and sleep in test_host_loop_drives_supervised_fixture_serve. The new message adds a later window and some more soak test names, but asks for the same change on the same tests. It reports only slow tests: no failure, no timeout and no wrong runtime behavior. The finding itself warns that sharing a soak run or faking the clock could drop the real serve and process coverage these tests exist to provide. Reopen if these tests cause a reachable harmful result, such as Check runs hitting the pytest timeout or the drain ceiling, or a Check attempt failing because of their run time.

- declined-box-000392-7c3e7668 declined speeding up the daemon-soak integration tests, including test_daemon_soak_is_rederivable
- tombstone-box-000394-411a2f41 already linked a repeat report on test_daemon_soak_is_rederivable to 000392
- declined-box-000395-70ebe69b declined a fake clock and sleep for test_host_loop_drives_supervised_fixture_serve
- The message reports durations only (17-27.5s per test) and no failed, timed-out or killed run
- The message's overcorrection_risk says the proposed fix could remove real serve and process coverage

Message: box-000406-61977fb8
