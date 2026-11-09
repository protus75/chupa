---
id: tombstone-box-000302-0c13ca18
kind: tombstone
link: declined-box-000299-84e19a9f
reopen_after_days: 30
---
The report says four tests in tests/test_seeded_phase7_core.py failed on base 868d2b4f because the retired ticket file tickets/phase7-continue/ticket.md was missing. Registry record 000299 already settled the same failure: that test module was removed from main, so the tests can no longer fail.

This is the same report as declined-box-000299-84e19a9f, with only the base commit changed. Records 000300 and 000301 were tombstoned against 000299 for the same reason. Commit acf9f661 removed the test module, so no current failure needs a repair.

- declined-box-000299-84e19a9f: tests/test_seeded_phase7_core.py was removed from main by commit acf9f661; no tracked test still refers to phase7-continue
- tombstone-box-000300-868b5f24 and tombstone-box-000301-18c81719 are the same report, tombstoned to 000299
- phase7-continue is retired and does not appear in the open tickets

Message: box-000302-0c13ca18
