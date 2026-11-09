---
id: declined-box-000183-57c38c91
kind: declined
link: box-000183-57c38c91
reopen_after_days: 90
---
A bootstrap review note says the one-time ingest of bootstrap suggestions, run as `python -m chupa.box` from the `suggestion-box` ticket's Verification during Check, wrote into the main checkout's `<state_dir>/box/` while the drain held the single-writer lock. The note itself calls this harmless because nothing else wrote the box at the time. It asks frozen-plan section 12 or 19.P2 to name the ingest as the allowed exception to the lock.

This asks for different plan wording, not a fix to current runtime behavior. The note itself says the write caused no harm. `CHUPA_PLAN.md` is frozen and is never edited, so the requested change cannot be made. The merged `remove-bootstrap-ingest` ticket removed the one-time ingest, so the lock bypass it describes can no longer happen. Record declined-box-000173-3c94a9a3 already declined a related request to name who runs this ingest in 19.P2.

- The message calls the write benign because nothing else wrote the box at the time.
- Merged stem `remove-bootstrap-ingest` removed the bootstrap ingest path.
- CLAUDE.md says CHUPA_PLAN.md is a frozen bootstrap design record and is never edited.
- declined-box-000173-3c94a9a3 declined a related plan-wording request about who runs the same ingest.

Message: box-000183-57c38c91
