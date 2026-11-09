---
id: tombstone-box-000318-8bfc4261
kind: tombstone
link: declined-box-000317-c455951f
reopen_after_days: 30
---
An Implement run (origin prompts-drop-plan) reports that `tests/test_cli.py::test_retro_doctor_entry_unit` fails. The cause it gives is that the merged phase5-continue-04 ticket's Context still names `tests/test_seeded_phase3_core.py`, which no longer exists.

This is the same failing test with the same cause, a stale reference in the phase5-continue-04 ticket to the removed `tests/test_seeded_phase3_core.py`, that registry record declined-box-000317-c455951f already decided. Only the reporting run differs (prompts-drop-plan here, core-host-neutral there). The message adds no new evidence.

- Message: test_retro_doctor_entry_unit fails because tickets/phase5-continue-04/ticket.md references missing tests/test_seeded_phase3_core.py
- Registry declined-box-000317-c455951f: identical failure and cause reported by a core-host-neutral Implement run, also reproduced on its base commit
- prompts-drop-plan is merged; the report is a pre-existing base failure surfaced during its Implement stage

Message: box-000318-8bfc4261
