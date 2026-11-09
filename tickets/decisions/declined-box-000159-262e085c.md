---
id: declined-box-000159-262e085c
kind: declined
link: box-000159-262e085c
reopen_after_days: 90
---
A spine-harvest review note warned that the harvest commit could carry any leftover outbox file, because the harvest lift was not limited to harvest.json. Current code already limits it: `chupa/runner.py:462` calls `lift_outbox(..., only=f"attempts/{attempt}/harvest.json")`, so the harvest commit can only contain that one file.

The gap no longer exists in current code. The harvest lift is limited to the harvest file. The wider problem of unbounded outbox lifts on the `run-record`, `review` and `checks` paths is already covered by the open ticket `outbox-lift-named-artifact-only`.

- chupa/runner.py:462: `await lift_outbox(ctx, stem, kind, attempt=attempt, only=f"attempts/{attempt}/harvest.json")`
- chupa/stages.py:484: `lift_outbox` takes `only` and passes it to `_lift_files`, which filters by it
- The open ticket outbox-lift-named-artifact-only covers the lifts that pass `only=None` (stages.py:657, 670, 1413, 1502)

Message: box-000159-262e085c
