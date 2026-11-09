---
id: tombstone-box-000309-3677fa33
kind: tombstone
link: declined-box-000306-c41256c4
reopen_after_days: 30
---
The attempts-cap run reports that the daemon merge-result path could start a rework on the failure that uses up the attempts cap, before that final failure is recorded, and says a daemon.py change is needed to stop it.

Registry record 000306 already decided this concern. The daemon merge-result path is TicketWriter.consume_result calling consume_handoff, and current code checks the cap before any rework: consume_handoff calls spent(..., pending={"to": outcome}) and calls apply_rework only when no cap is spent. The non-handoff branch never reworks.

- chupa/daemon.py:457-465 consume_result sends a ConflictHandoff to consume_handoff and other non-ok results straight to harvest_failure/failure_terminal
- chupa/daemon.py:477-478 calls apply_rework only if spent(ctx.config.caps, journal, stem, pending={"to": outcome}) is falsy
- declined-box-000306-c41256c4 covers the same daemon merge-queue result path and the same pending-failure cap check

Message: box-000309-3677fa33
