---
id: declined-box-000110-c4128c33
kind: declined
link: box-000110-c4128c33
reopen_after_days: 60
---
The note describes a crash window in `lift_outbox` (`chupa/stages.py:497-506`). Inside the `commit` effect, each outbox file is written to the canonical ticket dir and its source is unlinked before `git add`/`git commit` run and before the effect completion is journaled. If the process dies in that window, a replay sees an empty outbox, `_lift_files` returns nothing, and `lift_outbox` returns None. The canonical files then stay uncommitted in the main checkout. The note asks only for a test pinning that replay behavior once reconcile exists.

The window does exist in current code, but the request is test-only, and the note says to do it later, when reconcile lands. It reports no observed crash that left uncommitted ticket-plane artifacts on main, and no later stage or merge that failed or misbehaved because of them. Without such an incident this is speculative hardening plus test coverage, which the admission bar declines. The open ticket `outbox-lift-named-artifact-only` edits `lift_outbox` but deals with what gets lifted, not crash ordering, so this is not a duplicate.

- chupa/stages.py:499-505: `ctx.fs.write(...)` and `src.unlink()` run for each file before `ctx.git.add` and `ctx.git.commit`, all inside the effect action, so nothing is journaled until the commit returns.
- chupa/stages.py:492-494: `_lift_files` runs before the effect key is checked, so after a crash between unlink and journal, a replay finds an empty outbox and returns None without calling `effects.run`.
- The message gives no incident, run artifact or journal evidence that this crash happened or caused harm downstream.
- The proposed action is to add a test once reconcile lands, which makes it a test-only improvement.

Message: box-000110-c4128c33
