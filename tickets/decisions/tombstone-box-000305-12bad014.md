---
id: tombstone-box-000305-12bad014
kind: tombstone
link: declined-box-000299-84e19a9f
reopen_after_days: 30
---
An Implement run with origin verdict-human-only stopped with premise_failed. It reported that four tests in tests/test_seeded_phase7_core.py fail on the base commit because the retired ticket file tickets/phase7-continue/ticket.md is missing. Record 000299 already decided this failure. Records 000300 to 000304 already tombstoned the same report from other runs.

This report says the same thing as registry record declined-box-000299-84e19a9f. That record found that commit acf9f661 removed tests/test_seeded_phase7_core.py from main and that no tracked test still refers to phase7-continue. The failure therefore cannot happen on current main. Five earlier tombstones (000300 to 000304) linked the same report to record 000299. Only the origin and the base commit differ here, which is not a new behavior gap.

- declined-box-000299-84e19a9f: the test module was removed in commit acf9f661, and no tracked test refers to phase7-continue
- tombstone-box-000300-868b5f24 through tombstone-box-000304-331e614a: the same report from other base commits and origins, each linked to record 000299
- phase7-continue is retired and does not appear among the open tickets

Message: box-000305-12bad014
