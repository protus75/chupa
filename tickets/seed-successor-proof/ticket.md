---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- phase2-exit

## Context
- tests/test_seed_path.py
- tests/test_drain.py
- chupa/drain.py

## Plan contract
- 19.L
- 19.P3

## Goal / Why
Prove that a merged ticket registers its successor through the real seed lift, ticket intake, and the same running drain's re-scan, end to end. `tests/test_seed_successor.py` owns the proof; the production paths already exist.

## Scope in / Scope out
- In: a test runs the production drain with a predecessor dispatched through the real `drive` pipeline. Its Check reviews and lifts a successor authored `confirmed`/`seed`; after the predecessor merges, that running drain's tickets-directory re-scan makes the successor eligible and dispatches it within the same invocation. Assert the one seed commit, journal intake provenance, and dispatch order from the durable records.
- Out: changes to seed-lift, intake, drain, or scheduler machinery.

## Scope fence
- tests/test_seed_successor.py

## Acceptance criteria
1. `tests/test_seed_successor.py` demonstrates a predecessor's approved new successor reaches main in one `chupa(<stem>): seeds` ticket-plane commit, with a `ticket_intake` signal naming the predecessor and its committed seed blob.
2. `tests/test_seed_successor.py` demonstrates the real drain re-scans after that predecessor merges and dispatches the dependent successor in the same invocation, with the predecessor's `to: merged` record before the successor's dispatch.
3. `uv run pytest -q` exits 0 without removing or skipping a test.

## Verification
```
uv run pytest -q tests/test_seed_successor.py
uv run pytest -q
```

## Definition of rejected
Reject if the proof calls only a mocked seed lift or a mocked re-scan, if it commits a successor outside the ticket-plane lane, or if the diff leaves the fence.

## Time budget
- expected: 60m
- stuck: 90m
