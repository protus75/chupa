---
id: declined-box-000040-be7b15fb
kind: declined
link: box-000040-be7b15fb
reopen_after_days: 90
---
A bootstrap note said the driver called the LLM seam directly instead of going through `Effects.run`. It asked that the first LLM call site use an `llm/...` effect key and scrub the model text with the shared `Redactor` before the completion record is written. Current code already does this. `chupa/llmeffect.py` `llm_call` builds a key of the form `llm/<stem>/<run_seq>/<surface>/<attempt>/<call_seq>`, runs `redactor.scrub(result.text)` inside the action, and calls `effects.run(action, key=key, ticket=ticket, cost=_cost)`.

The gap the note describes is already closed, so there is nothing to build. The only difference is that the real key also includes `run_seq`, which makes it more specific than the proposed key, not less. No reachable runtime behavior is wrong. The registry already has related decisions on scrubbing inside the action (decision-box-000008-8732a7a8 area, box-000008) and on cost wiring (box-000007), so no new ticket is needed.

- chupa/llmeffect.py:3 docstring: keyed `llm/<stem>/<run_seq>/<surface>/<attempt>/<call_seq>`
- chupa/llmeffect.py:30 `redactor.scrub(result.text)` runs inside the action, before the completion is recorded
- chupa/llmeffect.py:32 `return await effects.run(action, key=key, ticket=ticket, cost=_cost)`
- decision-box-000008-cf8cefbd: `llm_call` scrubs the model text inside its action before `effects.run`
- decision-box-000007-a0b6c144: `chupa/llmeffect.py` passes a cost projection into `effects.run`

Message: box-000040-be7b15fb
