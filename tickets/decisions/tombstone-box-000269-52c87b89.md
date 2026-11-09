---
id: tombstone-box-000269-52c87b89
kind: tombstone
link: declined-box-000177-61a7474f
reopen_after_days: 90
---
This handoff note says ticketless triage calls would share one LLM effect key and replay each other if `Driver.run` always took `run_seq` from the journal. The merged `box-triage` work added a `run_seq` override for ticketless calls. The note asks the frozen plan (section 6 or 19.P2) to document that override.

Registry record declined-box-000177-61a7474f already decided this request. It covers the same triage key collision, the same `run_seq` override added by `box-triage`, and the same request to pin it in plan section 6 or 19.P2. The note reports no current runtime failure: the override has shipped. `CHUPA_PLAN.md` is also frozen and never edited, so the plan change cannot be made.

- Decision registry entry declined-box-000177-61a7474f describes the same ticketless triage effect-key collision and the same request to pin the `run_seq` override in plan section 6 or 19.P2.
- `box-triage` is in the merged stems, and the message says it already added the `run_seq` override in `chupa/driver.py`.
- Project rules say `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.

Message: box-000269-52c87b89
