---
id: declined-box-000064-cd2b120e
kind: declined
link: box-000064-cd2b120e
reopen_after_days: 90
---
A bootstrap note records two facts. In `chupa/config.py` `_check_references`, the check that Implement must route to a `kind: cli` provider runs before the api-provider refusal, because that rule will still apply after the api client ships. The api-refusal test in `tests/test_config.py` routes `review` so it tests only the api refusal. The note describes the design and reports no defect.

The note describes how the code is laid out and does not report a behavior gap. Current code matches it: `config.py:442-456` checks implement-requires-cli first, with a why-comment, then refuses `kind: api`. Both checks fail closed and show the operator a paved-road message. Nothing here shows reachable incorrect runtime behavior, so no ticket is warranted.

- chupa/config.py:442 comment: 'Before the api refusal: routing Implement to api stays wrong after the api client ships.'
- chupa/config.py:445-449 refuses an implement route to a non-cli provider with a paved-road message
- chupa/config.py:452-456 refuses kind: api until the api client ships
- The message reports no failure, stage, or outcome; it is a bootstrap-ingest design note

Message: box-000064-cd2b120e
