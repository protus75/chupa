---
id: declined-box-000306-c41256c4
kind: declined
link: box-000306-c41256c4
reopen_after_days: 30
---
The note says the daemon's merge-queue result path (`TicketWriter.consume_result` → `consume_handoff`) skips the pending-failure cap check that `drive` does, so it could rework a ticket on the failure that uses up its attempts cap. In current code the check is there: before `apply_rework` runs, `consume_handoff` calls `spent(..., pending={"to": outcome})`.

The gap the note describes is not in current code. `chupa/daemon.py:477` runs `apply_rework` only when `spent(ctx.config.caps, journal, stem, pending={"to": outcome})` returns None. That check stops rework when any cap is spent, counting the failure now being recorded. It is stricter than `drive`'s `== "attempts"` check at `chupa/runner.py:227`, so the fifth failure cannot reach rework. The other branch of `consume_result`, for a non-ok `StageResult`, calls only `harvest_failure` and `failure_terminal` and never starts rework. Nothing shows a current run doing the wrong thing.

- chupa/daemon.py:457-465: consume_result sends a ConflictHandoff to consume_handoff; a non-ok StageResult goes only to harvest_failure and failure_terminal, with no rework
- chupa/daemon.py:477-478: consume_handoff calls apply_rework only when spent(..., pending={"to": outcome}) is falsy
- chupa/runner.py:227: drive's check is spent(..., pending=...) == "attempts"; the daemon's check refuses rework whenever any cap is spent, which covers the attempts case
- attempts-cap is merged, and the pending-aware spent() signature is in chupa/caps.py:55

Message: box-000306-c41256c4
