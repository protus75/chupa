---
id: declined-box-000007-a0b6c144
kind: declined
link: box-000007-a0b6c144
reopen_after_days: 90
---
A bootstrap note said `Effects.run` journaled only the call's result, with no cost fields on `effect_completion`, because no metered call existed yet. It proposed adding tokens, seconds, usd, provider and model once the first metered call landed. That has since happened: `chupa/llmeffect.py` passes a `cost` projection (usd, input_tokens, output_tokens, provider, model) into `effects.run`, and `chupa/status.py` adds up `effect_completion.body.cost.usd` to report spend.

The gap is closed in current code, so nothing harmful is happening now and there is no ticket to write. The only listed field the projection leaves out is `seconds`, and the message gives no evidence that anything reads it or that its absence causes wrong behavior. That makes it speculative, not a behavior gap. I chose decision over tombstone because I could not tie the fix to one specific merged stem.

- chupa/llmeffect.py:20-21 `_cost` projects usd, input_tokens, output_tokens, provider, model
- chupa/llmeffect.py:32 `effects.run(action, key=key, ticket=ticket, cost=_cost)`
- chupa/status.py:64 sums `e.body["cost"]["usd"]` over EFFECT_COMPLETION events for spend

Message: box-000007-a0b6c144
