---
id: declined-box-000278-70140c4c
kind: declined
link: box-000278-70140c4c
reopen_after_days: 30
---
Reconcile reaps an orphan that has an effect intent but no `running` transition by journaling `to: abandoned`. The journal auditor in `chupa/audit.py` then reports a `one_terminal_per_run` violation because that terminal has no open run. The engine's recovery behaves correctly. The only mismatch is between the auditor's invariant and reconcile's intent-only reap.

The finding is real. `reconcile.py` treats an intent with no completion as an open run (line 18) and appends `abandoned` (line 52). `audit.py` flags a terminal with no prior `running` (lines 80-88). The auditor runs only in tests and eval harnesses (`eval/daemon_soak.py`, `eval/reliability_battery.py`, `eval/host_loop.py`, `eval/shakeout/run.py`, `tests/integration`). No engine runtime path calls it. No dispatch, cap, merge or recovery decision depends on it. `tests/integration/test_restart_timers.py:253-256` already pins this violation on purpose with a comment. So no runtime behavior is wrong today, and the change would be an auditor or test alignment. It would earn a ticket only if a soak or battery run actually failed on this false violation.

- chupa/reconcile.py:18,38: open runs include stems with an uncompleted intent and no `running` transition
- chupa/reconcile.py:52: reap appends `{"to": "abandoned"}` without a preceding `running`
- chupa/audit.py:80-88: a terminal with no open run is reported as `one_terminal_per_run` (only `rejected` is exempt)
- tests/integration/test_restart_timers.py:253-256 asserts this exact violation and documents it as known
- audit_journal callers are only in eval/ and tests/; no module under chupa/ imports chupa.audit

Message: box-000278-70140c4c
