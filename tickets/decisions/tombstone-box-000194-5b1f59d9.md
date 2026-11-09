---
id: tombstone-box-000194-5b1f59d9
kind: tombstone
link: declined-box-000007-a0b6c144
reopen_after_days: 90
---
This note says `effect_completion` records only the result and asks for cost fields (tokens, seconds, usd, provider, model) once the first metered call exists. Registry record 000007 already settled the same gap: the cost projection now exists and `effects.run` receives it.

This is the same suggestion as declined-box-000007-a0b6c144: add cost capture to `Effects.run` and `effect_completion` once a metered call lands. That record found the metered call has landed and the cost fields are already recorded, so this message adds nothing new.

- Registry record declined-box-000007-a0b6c144: `chupa/llmeffect.py` passes a `cost` projection (usd, input_tokens, output_tokens, provider, model) into `effects.run`.
- Registry record declined-box-000007-a0b6c144: `chupa/status.py` sums `effect_completion.body.cost.usd` to report spend.
- The message origin is bootstrap-ingest, the same source and wording as box-000007.

Message: box-000194-5b1f59d9
