---
id: tombstone-box-000203-0ea3b8df
kind: tombstone
link: migrate-config
reopen_after_days: 90
---
The note warned that the config loader's refusal of an older schema_version names `chupa migrate-config` before that verb was built, which would leave the manual 0->1 schema_version rewrite as the only way forward. It asked whether the plan's "never name an unbuilt verb" rule covers load refusals. The merged `migrate-config` ticket built the verb, so the refusal now names a command the operator can run.

This is the same concern as registry record tombstone-box-000023-78bfaf61, which links to the merged `migrate-config` ticket. The verb the refusal names now exists, so the refusal no longer names an unbuilt verb. Whether the rule covers load refusals no longer matters for this case, and nothing behaves incorrectly at runtime.

- Registry record tombstone-box-000023-78bfaf61 describes the same gap: the older-schema_version refusal names `chupa migrate-config` before the command existed, leaving only the manual 0->1 step.
- `migrate-config` appears in the merged stems list.
- Declined record 000025 says the config rewrite in `migrate-config` already goes through the FileSystem seam's write and replace, which confirms the verb is built.

Message: box-000203-0ea3b8df
