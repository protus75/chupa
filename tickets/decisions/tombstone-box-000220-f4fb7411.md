---
id: tombstone-box-000220-f4fb7411
kind: tombstone
link: tombstone-box-000059-07864ba4
reopen_after_days: 90
---
The CLI provider adapter writes its own scrubbed stdin prompt file under the providers spool, because `LLMRequest` carries no spool path. The suggestion asks to pass it the driver's spooled prompt path instead, and to key event-stream and stderr capture by attempt rather than by a sequence number kept inside each client process.

This repeats registry record tombstone-box-000059-07864ba4, which covers the same three points: the adapter's own prompt file, the driver's spooled file as the stdin channel, and moving capture into the per-attempt spool directory. That record chains to declined-box-000039-af7f01a0, which decided the adapter's own spool file makes a `prompt_path` field unnecessary. The per-attempt capture half is also covered by tombstone-box-000158-1bee1d13. The message gives no new evidence of harmful runtime behavior.

- Registry tombstone-box-000059-07864ba4: the same adapter prompt-file and per-attempt capture proposal
- Registry declined-box-000039-af7f01a0: decided the adapter writes its own spool file, so a `prompt_path` field is not needed
- Registry tombstone-box-000158-1bee1d13: the same request to key provider capture by attempt

Message: box-000220-f4fb7411
