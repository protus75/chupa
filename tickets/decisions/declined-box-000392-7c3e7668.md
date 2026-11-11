---
id: declined-box-000392-7c3e7668
kind: declined
link: box-000392-7c3e7668
reopen_after_days: 30
---
A retro over 25 runs found that two daemon-soak integration tests set the critical path of the parallel integration suite. test_daemon_soak_command_writes_report_only_on_green takes up to 31.6s and test_daemon_soak_is_rederivable takes up to 22.3s, in suite runs of 54-81s. The finding proposes speeding these tests up.

This is a test-speed finding. It shows no incorrect runtime behavior: the tests pass, and no run failed, timed out or parked because of them. A slower suite costs some wall time per Check, but nothing shows it caused a wrong outcome. The finding's own overcorrection note says that shrinking the fixtures or faking time would remove the real-subprocess, real-serve load these tests exist to apply. That load is what exposed the publication race fixed by soak-test-publication-race. So the obvious repair risks weakening a guard that has already caught a real bug. No open ticket or registry record covers this. Reopen if these tests cause a timeout, a pytest-timeout kill, a stuck-budget breach or a Check failure, or if suite wall time reaches a configured ceiling.

- retro/37: test_daemon_soak_command_writes_report_only_on_green peaks at 31.6s and test_daemon_soak_is_rederivable at 22.3s, against suite wall times of 54-81s in all 25 runs
- test_issue is 'slow'. The finding reports no failure, timeout or wrong outcome.
- overcorrection_risk: soak-test-publication-race surfaced only under real-subprocess, real-serve load
- No open ticket or decision record covers soak test runtime

Message: box-000392-7c3e7668
