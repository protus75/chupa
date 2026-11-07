---
id: decision-box-000044-79b4ca8b
kind: decision
link: box-000044-79b4ca8b
reopen_after_days: 90
---
This note asks for the journal writer to be built with the shared `Redactor`, so that secrets in effect results never reach the journal. Decision 000008 already settled the same question: the only journal producer that can carry secrets is the LLM effect result, and `llm_call` scrubs it before `effects.run` writes the completion record. The other `effects.run` callers write records built from engine data.

This repeats decision-box-000008-cf8cefbd, which asked for one scrub at the journal or effects write seam and was declined because callers already scrub. The current code still matches that decision. The `chupa/redact.py` checklist marks the journal writer as not wired, and says its one secret-bearing producer is scrubbed in `chupa/llmeffect.py` `llm_call`. Neither the message nor the code shows a secret ever reaching the journal, so there is no harmful behavior to fix.

- chupa/journal.py contains no reference to Redactor or redactor
- chupa/redact.py:7-8 lists the journal writer as 'NOT YET WIRED; its one secret-bearing producer, the LLM effect result, is scrubbed before it becomes the completion record (chupa/llmeffect.py `llm_call`)'
- decision-box-000008-cf8cefbd covers the same scrub-at-the-journal-seam proposal and records that callers scrub before effects.run
- decision-box-000040-be7b15fb confirms llm_call runs redactor.scrub(result.text) before effects.run
- unresolvable link: decision-box-000008-cf8cefbd

Message: box-000044-79b4ca8b
