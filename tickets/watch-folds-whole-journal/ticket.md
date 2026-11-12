---
priority: P0
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/observe.py::journal
- chupa/observe.py::text_snapshot
- chupa/__main__.py
- tests/integration/test_watch.py

## Goal / Why
`chupa watch` lists long-merged tickets as "ready, not run yet" (Queue 132 to do on 2026-11-11, including `plan-contract-section-render`, merged 2026-10-05, and every `harden-*` stem). Cause: `text_snapshot` in `chupa/observe.py` calls `journal(state)` with the default `limit=20000`. It folds `last_state` from those events and passes it to `queue(...)` and `held(...)`. The journal holds 25374 events, so a stem whose last transition falls before the newest 20000 has no settled state and is listed as pending. The other two journal readers, the snapshot in `observe.py` and `chupa/__main__.py`, already pass `limit=10**7` and are correct.

Class fix: no projection that folds ticket state may read a truncated journal. After this change `journal(state)` takes no `limit` parameter and always returns every event of every segment. Truncation stays only in `read_lines`, which is used for the `engine.log` display tail.

## Scope in / Scope out
- In: `chupa/observe.py`: `journal(state)` drops its `limit` parameter and returns all events from all segments in order. The snapshot caller drops `limit=10**7`. `read_lines` keeps its `limit` for `engine.log`.
- In: `chupa/__main__.py`: the `observe.journal(config.state_dir, limit=10**7)` call drops the `limit` argument.
- In: `tests/integration/test_watch.py`: a test that writes a journal with a `merged` transition for one stem followed by more than 20000 filler events, then calls `watch.text_snapshot(ctx)`.
- Out: journal segment format, `read_lines` behavior, queue/held logic, performance work such as incremental reads.

## Scope fence
- chupa/observe.py
- chupa/__main__.py
- tests/integration/test_watch.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py` exits 0. It includes a test where the stem's `merged` transition lies more than 20000 events before the journal end. The test asserts that the `text_snapshot` output does not list that stem under `Queue`; it fails on the old code, where the stem is listed as pending.
2. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_watch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `journal` still accepts a `limit` parameter or default that truncates events;
- `text_snapshot` raises its default limit instead of removing it;
- the new test also passes with the 20000-event default restored.

## Time budget
- expected: 20m
- stuck: 60m
