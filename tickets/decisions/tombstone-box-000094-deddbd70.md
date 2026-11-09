---
id: tombstone-box-000094-deddbd70
kind: tombstone
link: declined-box-000093-e1f5e684
reopen_after_days: 60
---
The note says `status` cannot show tickets that fail parsing as their own category at the top of its output. Intake returns a refusal to its caller and never journals it, so a status view built only from the journal never sees refused tickets. It suggests either journaling a refusal signal from intake or letting `status` lint the ticket files on disk without changing them.

Registry record 000093 already covers the same gap: intake refusals are returned to the caller and never journaled or logged, so anything that is not the synchronous caller (the drain and serve loops, and so the status projection) never names a refused stem. That record already weighed an intake signal as the fix. This note restates the same missing refusal signal from the `status` side, and it reports no new harm: `run` and `new` still print the findings to the operator at the moment of refusal.

- The note says Phase 1 intake refusals are returned to the caller and never journaled, so a projection built only from the journal cannot show them.
- Registry record declined-box-000093-e1f5e684 says drain and serve ignore `IntakeResult.refused` and asks for refused stems to appear in the engine log or an intake signal. That is the same missing signal.
- The note says `run` and `new` already print refusal findings synchronously, so a refusal is visible to the operator who triggered it.
- No open or merged ticket adds a journaled intake-refusal signal or a parse-failure category to `status`.

Message: box-000094-deddbd70
