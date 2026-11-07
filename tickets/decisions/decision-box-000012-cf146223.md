---
id: decision-box-000012-cf146223
kind: decision
link: box-000012-cf146223
reopen_after_days: 90
---
Each time `Effects.run` replays a completed key, `_recorded` in `chupa/effects.py` reads and parses the whole journal again to find that key's result. The suggestion is to cache results keyed by effect key during the startup scan, once replay volume makes the cost matter.

This is a performance idea, not a behavior gap. Replay returns the correct recorded result and raises if the completion event is missing. The suggestion itself makes the change conditional on replay volume mattering, and no measured slowdown, timeout, or watchdog incident from replay cost has been reported. Caching results would also make every Effects object hold all recorded results in memory, which is speculative accretion with no incident behind it. Reopen if a run record or the engine log shows replay time from repeated full-journal reads hurting a drain or serve run, for example startup or recovery slowing in proportion to journal size times replayed keys.

- chupa/effects.py:21 startup scan stores only the set of completed keys
- chupa/effects.py:33-34 a replayed key calls self._recorded(key)
- chupa/effects.py:49-53 _recorded walks self._journal.read() until it finds the matching EFFECT_COMPLETION and returns body['result'], so results are correct
- No open ticket, merged stem, or decision covers replay lookup cost; decision-box-000011 (shared Effects per session) is related but separate

Message: box-000012-cf146223
