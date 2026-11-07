---
id: decision-box-000010-e476a678
kind: decision
link: box-000010-e476a678
reopen_after_days: 60
---
`Effects.run` checks for a completed key and only records it after its action finishes. Two calls with the same key running at the same time in one event loop could therefore both run the action, because nothing guards a key that is still in progress. The note asks for a per-key asyncio lock or an in-flight set, plus a test, once some caller runs effects concurrently.

The race exists in the code but nothing shows any caller can trigger it. Every current key is tied to one ticket and one attempt (`merge/<stem>/<attempt>`, `ticket-plane/<stem>/<attempt>/rework`, `ticket-plane/<stem>/author`), to one message (`ticket-plane/decisions/<record_id>`, `<escape>/<message.id>`), or is a retro sequence or notification identity. Each one runs in a single sequential path for that ticket or message. The daemon runs concurrent workers, but they work on different tickets, so their keys never collide. No incident or journal record shows the same key executed twice. As things stand this is speculative hardening, not a harmful gap that can happen today.

- chupa/effects.py:33-46 checks `key in self._completed` before `await action()` and adds the key only after the completion is appended, so no in-flight guard exists
- Effects.run call sites (stages.py:509, merge.py:328, daemon.py:394, author.py:131/302, triage.py:66/246, retro.py:233, checkpoint.py:133, notify.py:27, llmeffect.py:32) use keys scoped to a ticket and attempt, a message, a retro sequence, or a notification identity
- daemon.py runs concurrent workers on separate tickets, so their effect keys are disjoint
- No reported incident of a duplicate effect execution or duplicate effect_completion for one key

Message: box-000010-e476a678
