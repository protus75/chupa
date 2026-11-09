---
id: declined-box-000299-84e19a9f
kind: declined
link: box-000299-84e19a9f
reopen_after_days: 30
---
The note reported that four tests in tests/test_seeded_phase7_core.py failed because the retired tickets/phase7-continue/ticket.md was missing. On current main that test file no longer exists. Commit acf9f661 removed it, and no tracked test still refers to phase7-continue, so the suite no longer has these failures.

There is no current behavior gap. The failing tests were tied to a ticket that has been retired, and commit acf9f661 ('Unblock the post-bootstrap tickets') deleted the test file. The only remaining reference is a stale __pycache__ .pyc, which is untracked and is not collected as a test.

- `ls tests/test_seeded_phase7_core.py` on main: No such file or directory
- `git log -- tests/test_seeded_phase7_core.py`: last touched by acf9f661, which removed the file
- tickets/phase7-continue was retired in 347c9704, and its directory is gone in acf9f661
- `grep -rln phase7-continue tests` matches only tests/__pycache__/test_seeded_phase7_core.cpython-314-pytest-9.1.1.pyc

Message: box-000299-84e19a9f
