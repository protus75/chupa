---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-13

## Context
- chupa/daemon.py
- chupa/config.py
- chupa/seams.py
- chupa/__main__.py

## Plan contract
- 19.I
- 19.P3.heartbeat
- section 9
- section 15

## Goal / Why
Construct the dormant heartbeat component governed by 19.P3.heartbeat so an explicitly invoked cycle and an external freshness check can demonstrate core liveness through injected seams.

## Scope in / Scope out
19.P3.heartbeat is the complete governing contract for Owner, Records, Observable and every named Tests obligation, including record custody; implement all of it. The renderer injects those bullets verbatim. Implement the new chupa/heartbeat.py under that unit's Owner, and the explicitly invoked boundary in chupa/daemon.py under the same Owner. Never copy unit text into this seed or invent records or owners.

The registry floor needs no additions: preserve DaemonTasks, DaemonAdmission, daemon_core and build_daemon_core signatures and ownership, Config.state_dir, FileSystem.write and Clock. Read their direct callers and the merged production-composition harness before writing. Greps across chupa/, eval/ and tests/ found no heartbeat caller, public-operation allowlist or old assertion this dormant construction must flip. Keep ordinary DaemonTasks exception propagation and cleanup and bootstrap inline admission. Existing chupa/daemon.py is embedded Context; the two new fenced paths are created, never Context or On-demand.

Prove behavioral dormancy with calibrated raising construction/cycle probes over real CLI run/drain and the merged production-composition harness: deliberate wiring must trip the probe and ordinary composition must leave it untouched. chupa.daemon is already reachable; import absence is not dormancy evidence. Use injected seams, scripted health/metadata callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Exercise the actual dormant component directly, including each named invariant and custody obligation in the cited entry unit. serve-activation owns heartbeat production wiring and dormancy migration.

The existing tests/test_daemon_tasks.py, tests/test_daemon_composition.py, tests/test_cli.py and tests/test_drain.py are unchanged preservation suites in Verification only, neither fenced nor embedded. Out: background startup, serve wiring, altered signatures, changed verification results, replacement control/abort paths or task graphs, unearned records, plan/registry changes, existing tickets/run records and historical seeding tests.

## Scope fence
- chupa/heartbeat.py
- chupa/daemon.py
- tests/test_heartbeat.py

## Acceptance criteria
1. `uv run pytest tests/test_heartbeat.py tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py` exits 0 with test_construction_is_idle, test_healthy_cycle_refreshes_heartbeat and test_unhealthy_core_stops_refresh proving the complete 19.P3.heartbeat construction/cycle contract and record custody.
2. `uv run pytest tests/test_heartbeat.py tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py` exits 0 with test_heartbeat_failures_propagate, test_external_heartbeat_freshness and test_external_heartbeat_refuses_invalid_evidence proving the complete cited external-check and failure contract.
3. `uv run pytest tests/test_heartbeat.py tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py` exits 0 with test_heartbeat_is_dormant proving calibrated real CLI run/drain and production-composition dormancy while preservation suites stay unchanged.
4. `uv run pytest -q` exits 0 without any test removed or skipped or any production heartbeat wiring.

## Verification
```
uv run pytest tests/test_heartbeat.py tests/test_daemon_tasks.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the omitted or contradictory 19.P3.heartbeat fact for section 11.4 hardening if the complete contract cannot be met, or if criteria force an unearned path outside the fence. Never invent records, replacement graphs or production wiring.

## Time budget
- expected: 60m
- stuck: 90m
