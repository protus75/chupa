---
id: declined-box-000147-ce29be8b
kind: declined
link: box-000147-ce29be8b
reopen_after_days: 90
---
A bootstrap re-entry review note asks for a test of re-offering a ticket after it ended `abandoned` or `infra_error` rather than `gate_failed`. In that case the re-entry block has no findings artifact and falls back to the text "no findings artifact; detail is in engine.log". The note asks for a test that pins this fallback.

This only asks for more test coverage. It reports no wrong runtime behavior: nothing shows the fallback text renders wrongly or that a re-offer after a non-gate_failed terminal misbehaves. Earlier test-only bootstrap notes were declined on the same grounds (000131, 000142, 000143, 000146).

- Message class is `suggestion` from bootstrap-ingest, with no stage, outcome or failure report.
- The message itself says the gap is a missing test ("pin that branch"), not a failure.
- Decisions declined-box-000142-bc91046d, declined-box-000143-1f820d8a and declined-box-000146-bd19e063 declined similar test-only drain and re-entry notes.

Message: box-000147-ce29be8b
