---
id: declined-box-000008-2cd1c599
kind: declined
link: box-000008-2cd1c599
reopen_after_days: 60
---
The note asks for one scrub inside `Effects.run`, between encoding the result and appending `effect_completion`, once the redaction seam exists. The seam now exists (`chupa/redact.py` `Redactor`), but callers already scrub before returning. `llm_call` scrubs the model text inside its action before `effects.run`, and the command-notification seam scrubs stdout and stderr. The other `effects.run` callers in checkpoint, daemon, stages, merge, author, retro and triage return commit SHAs or structured records built from engine data.

No secret is shown reaching an `effect_completion` record or an effect's return value. Free text that could carry a secret is already scrubbed at its source, so a central scrub in `Effects.run` would be speculative hardening and would redact twice on the LLM path. Under the admission bar this is a decision, not a ticket.

- chupa/effects.py:36-47 encodes the result and appends effect_completion without redaction
- chupa/llmeffect.py:30 scrubs result.text with the Redactor inside the action, before Effects.run records it
- chupa/seams.py:87 scrubs notification out/err; chupa/notify.py:27 routes it through effects.run
- The other effects.run callers (checkpoint.py:133, daemon.py:394, stages.py:509, merge.py:328, author.py:131/302, retro.py:233, triage.py:66/246) return commit SHAs or records built by the engine
- No open ticket or decision covers redacting effect results

Message: box-000008-2cd1c599
