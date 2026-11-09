---
id: tombstone-box-000362-d7a3fe40
kind: tombstone
link: declined-box-000361-1e0f1d0a
reopen_after_days: 30
---
An Implement run reported that ticket lint fails when run over the whole repository, because many existing tickets have stale Context paths or sections lint does not recognize.

Registry record 000361 already declined this same report: repository-wide ticket lint is red because older tickets have invalid sections and paths that no longer exist. The new message comes from another run (core-chat-ticket-first) and adds no new harm. It names no ticket the drain failed to dispatch or run, and no run that broke because of these stale tickets. Per-ticket `chupa lint <stem>` is the launch gate and still works. The one runtime-harmful case, a Context entry that names a directory and crashes Implement, is already covered by open ticket context-rejects-directory.

- declined-box-000361-1e0f1d0a: whole-repo ticket lint fails on existing tickets' invalid sections and missing paths
- message origin core-chat-ticket-first is a merged stem; the report is a second problem filed from its Implement run
- open ticket context-rejects-directory covers the reachable crash from a bad Context path

Message: box-000362-d7a3fe40
