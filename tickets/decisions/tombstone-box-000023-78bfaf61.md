---
id: tombstone-box-000023-78bfaf61
kind: tombstone
link: migrate-config
reopen_after_days: 90
---
This bootstrap note was worried that the config loader rejects an older schema_version and tells the operator to run `chupa migrate-config` before that command existed. That would leave the operator with only the manual 0->1 step as a way forward. The command now exists, so the error message names a command the operator can run.

Merged ticket migrate-config added the `chupa migrate-config` command. The refusal text that names it therefore points to a real command, and the question of whether the 'never name an unbuilt verb' rule covers it no longer arises. The manual fallback text is still in the message too.

- migrate-config is in the merged stems; commit e60f8023 'chupa(migrate-config): The strict loader's schema-zero repair road runs an explicit lossless, validated migration.'
- chupa/__main__.py:236 registers the `migrate-config` subcommand, and chupa/__main__.py:289-290 sends it to config.migrate_config
- chupa/config.py:305 defines migrate_config; chupa/config.py:386 refusal text names `chupa migrate-config` and still states the manual 0->1 step

Message: box-000023-78bfaf61
