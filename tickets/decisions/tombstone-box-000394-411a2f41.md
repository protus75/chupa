---
id: tombstone-box-000394-411a2f41
kind: tombstone
link: declined-box-000392-7c3e7668
reopen_after_days: 30
---
A retro finding reports that the integration test test_daemon_soak_is_rederivable in tests/integration/test_daemon_soak_runner.py takes up to about 21s in every one of 14 runs. It runs the full soak production twice against real git only to compare the two reports. The finding asks for the test to be made faster because it likely sets the critical path of the parallel integration suite.

Record declined-box-000392-7c3e7668 already settled this request. That retro finding named the same test, test_daemon_soak_is_rederivable (up to 22.3s), as one of two daemon-soak tests on the critical path of the parallel integration run, and it proposed speeding them up. This message only adds the double soak.produce call as the cause and lists sibling tests that run the same production. It is still a test-speed improvement with no incorrect runtime behavior, so the earlier decline stands. Reopen if the suite's run time causes a harmful outcome, such as Check or merge timeouts or a stuck-budget kill traced to this test.

- Registry declined-box-000392-7c3e7668: two daemon-soak integration tests set the critical path of the parallel integration suite, test_daemon_soak_is_rederivable up to 22.3s in 54-81s suite runs; the finding proposed speeding them up.
- This message: test_daemon_soak_is_rederivable up to 20.9s across 14 integration runs, calls soak.produce twice against SubprocessExec, test_issue=slow.
- The message's own overcorrection_risk says sharing a module-scoped fixture risks order dependence, and shrinking the horizon risks missing nondeterminism, so it names no incorrect runtime behavior.

Message: box-000394-411a2f41
