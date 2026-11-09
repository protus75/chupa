---
id: tombstone-box-000202-7e7a2e80
kind: tombstone
link: declined-box-000022-a109febf
reopen_after_days: 90
---
The note asks for a spec rule that says which top-level config keys are required and which are optional with defaults. Today `chupa/config.py` makes that split on its own judgment, so the loader cannot be rebuilt from the spec alone.

This repeats registry record declined-box-000022-a109febf, which already declined a written spec of the required and optional top-level config keys in `chupa/config.py`. The note shows no wrong runtime behavior. It only asks for the spec to state a split that the code already enforces.

- Registry record declined-box-000022-a109febf covers the same request: spec which top-level config keys are required and which have defaults, because config.py decides this itself.
- The message is a bootstrap-ingest suggestion about missing spec text and reports no failing config load.

Message: box-000202-7e7a2e80
