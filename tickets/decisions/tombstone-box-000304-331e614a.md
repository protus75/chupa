---
id: tombstone-box-000304-331e614a
kind: tombstone
link: declined-box-000299-84e19a9f
reopen_after_days: 30
---
A ticket run stopped at implement with premise_failed, origin ticket-changed-midrun. It reported that on base ef2ceca3 four tests in tests/test_seeded_phase7_core.py fail because the retired tickets/phase7-continue/ticket.md is missing. Record 000299 already decided this same report. Records 000300 to 000303 tombstoned the same report seen from other base commits.

The report is the same failure as declined-box-000299-84e19a9f: the same test module, the same missing retired ticket file and the same four failures. Only the base SHA is different. On the current main checkout the test module no longer exists, so no current runtime gap needs its own ticket.

- The message names the same 4 failures in tests/test_seeded_phase7_core.py and the same missing tickets/phase7-continue/ticket.md as declined-box-000299-84e19a9f.
- A Glob for tests/test_seeded_phase7*.py in the main checkout found no files, so the module is gone from current main.
- Tombstones 000300, 000301, 000302 and 000303 already link this same report, from other base commits, to declined-box-000299-84e19a9f.

Message: box-000304-331e614a
