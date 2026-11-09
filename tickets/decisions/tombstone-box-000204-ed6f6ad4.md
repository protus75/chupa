---
id: tombstone-box-000204-ed6f6ad4
kind: tombstone
link: declined-box-000024-19e03301
reopen_after_days: 90
---
The config loader uses two bases for relative paths. `state_dir`, `worktree_root` and `report_inbox` resolve against the config file's directory, while `rules_doc` and `context_files` resolve against the checkout. The config spec section does not say which base applies. The note asks for the spec to state it.

Registry record declined-box-000024-19e03301 already covers this exact request: write down which base each relative config path resolves against. That record declined it. This message repeats the same bootstrap note and adds no new evidence of wrong runtime behavior.

- Registry record declined-box-000024-19e03301 describes the same split: state_dir/worktree_root/report_inbox resolve against the config dir, and rules_doc/context_files resolve against the checkout. Section 15 does not state it.
- The message origin is bootstrap-ingest and it reports no failure, stage or outcome.

Message: box-000204-ed6f6ad4
