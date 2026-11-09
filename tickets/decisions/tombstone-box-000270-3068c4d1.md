---
id: tombstone-box-000270-3068c4d1
kind: tombstone
link: declined-box-000183-57c38c91
reopen_after_days: 90
---
A handoff review note says the one-time bootstrap ingest (`python -m chupa.box`, run from the `suggestion-box` ticket's Verification during Check) wrote into the main checkout's `<state_dir>/box/` while the drain held the single-writer lock. It asks the frozen plan to name this ingest as the allowed exception to the lock.

Registry record declined-box-000183-57c38c91 already decided this request: same ingest, same lock overlap, same request for a plan exception. The note itself calls the overlap harmless. The bootstrap ingest has also since been removed (merged `remove-bootstrap-ingest`), and `CHUPA_PLAN.md` is frozen, so the requested plan change cannot be made.

- declined-box-000183-57c38c91 covers the same ingest-under-lock note and its request for an exception in section 12 or 19.P2
- Merged stem `remove-bootstrap-ingest` removed the one-time ingest path
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited
- The message itself calls the overlap benign because nothing else wrote the box at the time

Message: box-000270-3068c4d1
