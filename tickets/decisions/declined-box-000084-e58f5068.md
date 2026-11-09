---
id: declined-box-000084-e58f5068
kind: declined
link: box-000084-e58f5068
reopen_after_days: 90
---
A bootstrap review note says one deliverable's diff only moved `llm_call`, `llm_key` and `_cost` from `chupa/driver.py` into `chupa/llmeffect.py`. The effect's actual behavior (replay without a new call, one cost event per call, scrub before recording) arrived in an earlier wip commit, bb34134, and that diff's review never looked at it again.

The note is about review coverage during bootstrap. It reports no wrong runtime behavior. The behavior it says went unreviewed is now covered by tests and has been checked by earlier triage decisions. Decision 000040 confirmed that `llm_call` builds the `llm/...` key, scrubs the text before `effects.run`, and records cost. Decision 000007 confirmed that the cost projection is journaled and that `chupa/status.py` reads it. `tests/integration/test_llm_effect.py` pins each behavior the note names. No defect is shown, so there is nothing to build a ticket around.

- tests/integration/test_llm_effect.py:97 test_each_call_journals_exactly_one_cost_bearing_completion
- tests/integration/test_llm_effect.py:120 test_same_sequence_reentry_replays_without_recalling
- tests/integration/test_llm_effect.py:133 test_replay_survives_a_restart
- tests/integration/test_llm_effect.py:182 test_recorded_result_is_scrubbed_before_the_completion_and_the_return
- Decision declined-box-000040-be7b15fb: llm_call keys, scrubs and records through effects.run
- Decision declined-box-000007-a0b6c144: cost projection is journaled and read by status

Message: box-000084-e58f5068
