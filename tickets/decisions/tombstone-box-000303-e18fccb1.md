---
id: tombstone-box-000303-e18fccb1
kind: tombstone
link: declined-box-000299-84e19a9f
reopen_after_days: 30
---
The report says four tests in tests/test_seeded_phase7_core.py fail on the base commit because the retired ticket file tickets/phase7-continue/ticket.md is missing. Record 000299 already decided this same report. That test module is no longer on main, so these failures cannot happen.

This is the same failure that declined-box-000299-84e19a9f settled, and tombstones 000300 to 000302 repeated it. A check of the current tree shows tests/test_seeded_phase7_core.py is gone and no file under tests/ mentions phase7-continue. The reported failure therefore no longer happens, and nothing needs fixing.

- Registry record declined-box-000299-84e19a9f covers the identical report: commit acf9f661 removed the test module.
- Tombstones 000300, 000301 and 000302 point the same repeated report to record 000299.
- Searching for tests/test_seeded_phase7* in the current tree finds no files.
- Searching tests/ for 'phase7-continue' finds no matches.

Message: box-000303-e18fccb1
