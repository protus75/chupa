---
id: declined-box-000307-356acaee
kind: declined
link: box-000307-356acaee
reopen_after_days: 30
---
Report from the attempts-cap Implement run: the standalone `premise_park_release` shakeout member in `eval/` needs to set its own `premise_bounce` budget instead of relying on the config default, and `eval/` was outside that ticket's fence.

Current code already does this. `_premise_park_release` in `eval/shakeout/drain.py` sets `premise_bounce: 2` on its bench config, and the runner member in `eval/shakeout/runner.py` sets the same override. The member no longer depends on the shipped default, so nothing is broken and no ticket is needed.

- eval/shakeout/drain.py:48 sets `bench.config.caps.model_copy(update={"premise_bounce": 2})` inside `_premise_park_release`
- eval/shakeout/runner.py:35 sets the same `premise_bounce: 2` override
- eval/shakeout/drain.py:114 registers the `premise_park_release` member, which uses that override
- config.yaml:55 sets the shipped `premise_bounce` to 2

Message: box-000307-356acaee
