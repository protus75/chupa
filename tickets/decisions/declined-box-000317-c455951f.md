---
id: declined-box-000317-c455951f
kind: declined
link: box-000317-c455951f
reopen_after_days: 30
---
A core-host-neutral Implement run reported that `test_retro_doctor_entry_unit` failed because the merged phase5-continue-04 ticket's Context names `tests/test_seeded_phase3_core.py`, which no longer exists. The run said the same failure also happened on its base commit.

Current main no longer has this failure. No file under `tests/` defines `test_retro_doctor_entry_unit` or mentions `test_seeded`, `retro_doctor_entry` or `phase5-continue-04`. The only places these names still appear are historical ticket text and harvest records, and no test reads them. Plan grammar and seeding were removed (remove-plan-grammar, remove-seeding, remove-plan-text-tests), and that took the failing test with them. This is the same kind of stale seeded-test report as record 000299. No runtime behavior is wrong today.

- Grep of tests/ for 'retro_doctor_entry|test_seeded|phase5-continue-04' finds no matches
- No file matches tests/test_seeded*.py on main
- `test_retro_doctor_entry_unit` appears only in tickets/retro-doctor-cli/ticket.md:37
- `tests/test_seeded_phase3_core.py` is mentioned only in old ticket Context lists and attempt harvest.json files, which no test parses
- declined-box-000299-84e19a9f settled the same kind of failure: a removed seeded test module failing on a missing retired ticket

Message: box-000317-c455951f
