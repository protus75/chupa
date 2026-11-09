---
id: tombstone-box-000195-e9104abf
kind: tombstone
link: declined-box-000008-2cd1c599
reopen_after_days: 90
---
The note asks for one redaction scrub inside `Effects.run`, between encoding an effect's result and appending its completion record, so the returned value and the journaled record are the same scrubbed value. Registry record 000008 already settled the same request.

This repeats declined-box-000008-2cd1c599: same location (`Effects.run`), same seam (between encode and the completion append) and same trigger (once the redaction seam ships). Record 000008 found that the `Redactor` seam exists and that callers already scrub before returning. `llm_call` scrubs model text inside its action, command notifications scrub stdout and stderr, and the other `effects.run` callers return SHAs or records built from engine data. Records 000044 and 000082 reached the same conclusion for the journal-writer variant. The note shows no new evidence of an unscrubbed secret reaching a completion record.

- declined-box-000008-2cd1c599 covers the same scrub between encode and completion append in Effects.run
- declined-box-000040-be7b15fb: llm_call runs redactor.scrub(result.text) inside the action before effects.run records it
- declined-box-000044-79b4ca8b and tombstone-box-000082-e8c4a03a: no journal producer other than the already-scrubbed LLM result carries secrets
- Message origin is bootstrap-ingest and it reports no observed leak

Message: box-000195-e9104abf
