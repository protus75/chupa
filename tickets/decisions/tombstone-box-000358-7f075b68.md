---
id: tombstone-box-000358-7f075b68
kind: tombstone
link: declined-box-000344-8942f215
reopen_after_days: 30
---
After box-declined-verdict merged, the rename of `tickets/decisions/decision-*.md` records to the allowed kinds was left to the operator as a manual step and was not done. `read_registry` then raised a traceback on `kind: decision`, and every `chupa triage` crashed (2026-11-07). The note asks for two things: authoring should forbid manual post-merge operator steps, so that a migration covers every persisted record it invalidates, and `read_registry` should refuse with a paved road that names the bad file.

This repeats requests the registry has already decided. Record 000344 declined the same main point: a stored-state change from box-declined-verdict whose manual migration step broke readers until the operator ran it, with a request that pending manual migrations never break readers. Record 000339 covers the same crash on `kind: decision` records. Commit 20073cda has since renamed those records to the allowed kinds, and later runs finish ok, so nothing is broken now. The note brings no new reachable failure beyond what those records already decided.

- declined-box-000344-8942f215: box-declined-verdict shipped its migration as a manual `./dev.py migrate-box` step, and readers failed with a ValidationError until it ran (2026-11-07); the request to never break readers during a pending manual migration was declined.
- declined-box-000339-b4e8fec1: the forced retro failed loading `tickets/decisions/decision-box-000027-210a053d.md` because `kind: decision` is not `declined` or `tombstone`; commit 20073cda renamed the records and later retro runs finish ok.
- The current decision registry lists only `declined-*` and `tombstone-*` records, so no `kind: decision` record remains to crash `read_registry`.

Message: box-000358-7f075b68
