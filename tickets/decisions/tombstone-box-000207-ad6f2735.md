---
id: tombstone-box-000207-ad6f2735
kind: tombstone
link: declined-box-000030-f689a116
reopen_after_days: 90
---
The note proposes that config loading reject any `providers[].auth` value that is not an environment-variable name (`^[A-Z_][A-Z0-9_]*$`). The goal is to refuse a literal key pasted into config before the redaction seam has to catch it.

Registry record declined-box-000030-f689a116 already settled the same proposal: the same field, the same env-var-name regex and the same reason (refuse a pasted key at load rather than rely on redaction). The message adds no new evidence, such as a key that was actually pasted or one that leaked past the redactor.

- declined-box-000030-f689a116: config schema types providers[].auth as any string; proposal to reject values not matching ^[A-Z_][A-Z0-9_]*$ at load so a pasted key is refused before the redaction seam
- Incoming message (origin bootstrap-ingest) restates the same field, regex and rationale with no reported incident

Message: box-000207-ad6f2735
