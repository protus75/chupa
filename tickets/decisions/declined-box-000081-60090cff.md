---
id: declined-box-000081-60090cff
kind: declined
link: box-000081-60090cff
reopen_after_days: 90
---
For a ticket run, the LLM effect key has two slots, `<run_seq>` and `<attempt>`, that hold the same number. The note asks section 6 of the plan to define what `<attempt>` means for a ticket run. It also asks whether the driver should derive the spool attempt number from the journal fold instead of trusting the caller.

This asks for a spec definition and a possible hardening of where the attempt number comes from. It reports no wrong runtime behavior. A redundant key slot still produces unique, stable effect keys, and the note shows no collision, failed replay, or misplaced spool directory caused by a caller passing a number that disagrees with the fold. The plan is frozen, so a plan-wording fix cannot be authored. Registry record declined-box-000040-be7b15fb has already reviewed this key shape (`llm/<stem>/<run_seq>/<surface>/<attempt>/<call_seq>`).

- The message is class `suggestion` from `bootstrap-ingest`, with no stage, outcome, or failure report.
- The note itself says the two slots are redundant for a ticket run, which is a naming or clarity issue, not a fault.
- declined-box-000040-be7b15fb records that `chupa/llmeffect.py` `llm_call` already builds the key as `llm/<stem>/<run_seq>/<surface>/<attempt>/<call_seq>` and runs through `effects.run`.
- CLAUDE.md says `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited.

Message: box-000081-60090cff
