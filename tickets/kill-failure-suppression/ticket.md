---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-11
- kill-worker-stop

## Context
- chupa/daemon.py
- chupa/control.py
- chupa/driver.py

## Plan contract
- 19.I
- 19.P3.kill-failure-suppression
- section 20

## Goal / Why
Build the dormant kill-failure-suppression boundary governed by its own entry unit, ready for later serve activation.

## Scope in / Scope out
The cited 19.P3.kill-failure-suppression is the complete governing contract for Owner, Records, Observable and every named Tests obligation; implement all of them through the real predecessor boundaries. The renderer injects that unit verbatim. Do not copy unit bodies into this ticket. Authoring greps found no earned rule 2-5 addition: preserve the registry floor, existing Driver construction/run signatures, DaemonTasks construction/run and ownership, and ordinary failure routing. Existing fenced chupa/daemon.py is embedded; the new test belongs in neither Context nor On-demand. All predecessor suites in Verification are unchanged preservation suites, neither fenced nor embedded.

Construction remains behaviorally dormant through calibrated raising probes over real CLI run/drain and the merged production-composition harness. Deliberate wiring must trip each probe; ordinary composition leaves it untouched. Use injected seams, disposable directories and asyncio barriers. Out: CLI kill activation, concurrent polling, background startup, serve wiring, replacement control or abort paths, new durable flags or applied records, altered signatures, historical seeding tests and unrelated failure routing.

## Scope fence
- chupa/daemon.py
- tests/test_kill_failure_suppression.py

## Acceptance criteria
1. `uv run pytest tests/test_kill_failure_suppression.py tests/test_kill_worker_stop.py tests/test_daemon_tasks.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py` exits 0 with every named invariant in the cited own-entry Tests contract, proving its complete dormant obligations and record custody through real predecessor boundaries.
2. `tests/test_kill_failure_suppression.py` proves the own-entry Owner, Records and Observable obligations with calibrated raising production dormancy probes and protected cleanup; all preservation suites remain unchanged.
3. `uv run pytest -q` exits 0 with no tests removed or skipped and no production activation.

## Verification
```
uv run pytest tests/test_kill_failure_suppression.py tests/test_kill_worker_stop.py tests/test_daemon_tasks.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the omitted or contradictory entry-unit fact for section 11.4 hardening if its contract cannot be met inside the fence. Never invent a replacement graph, records or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
