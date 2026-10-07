---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-12

## Context
- chupa/daemon.py
- chupa/stages.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_kill_signal_journal.py
- tests/test_kill_executor_abort.py
- chupa/control.py
- chupa/driver.py
- chupa/runner.py

## Plan contract
- 19.I
- 19.P3.kill-cli-activation
- section 20

## Goal / Why
Activate the additive kill verb against the live bootstrap drain through its existing production executor and shared control inbox.

## Scope in / Scope out
The cited 19.P3.kill-cli-activation is the complete governing contract for Owner, Records, Observable and every named Tests obligation, including record custody; implement all of it through the real predecessor boundaries. The renderer injects that complete unit verbatim. Never copy unit text into this seed. This deep registry row starts high/high.

Authoring greps across chupa/, eval/ and tests/ covered abort_current, timeout ownership, optional review waits, cancellation handling, DaemonTasks task ownership, ordinary failure callbacks, public-operation allowlists, CLI verbs, production absence assertions, StageContext/TicketWriter forwarding, runner.bind, Pipeline/Dispatch and drain composition. The registry floor needs no additions under 19.L closure rules 2-5. Preserve Driver construction/run and all existing composition/callable signatures, the predecessor control implementation and executor abort path, and shared admission/dispatch hold semantics. The two predecessor dormancy assertions named by the entry unit are already fenced; migrate only those criteria-forced assertions, retaining their other invariants. Direct callers need no edits because signatures stay unchanged. Never migrate historical seeding tests.

Every fenced existing path is embedded Context. The created tests/test_kill_cli_activation.py belongs in neither Context nor On-demand. No embedding breaches the 300,000-character authoring headroom. All other suites are unchanged preservation suites in Verification only, neither fenced nor embedded. In particular worker-stop and failure-suppression remain dormant; serve-activation owns their production wiring and dormancy migrations. Preserve bootstrap inline admission and ordinary DaemonTasks exception propagation and cleanup.

Use calibrated raising probes over real CLI run/drain and the merged production-composition harness: deliberate wiring must trip the probe and ordinary composition must leave it untouched. chupa.daemon is already reachable; import absence is not dormancy evidence. Explicit tests use injected seams, scripted LLMs, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Read the preservation harness on demand as a reference without fencing or embedding it.

Out: worker boundary activation, background startup, serve wiring, replacement control/abort paths, a second executor or inbox, a new timer, failure route or task graph, altered signatures, unearned records and unrelated cleanup.

## Scope fence
- chupa/daemon.py
- chupa/stages.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_kill_signal_journal.py
- tests/test_kill_executor_abort.py
- tests/test_kill_cli_activation.py

## Acceptance criteria
1. `uv run pytest tests/test_kill_cli_activation.py tests/test_kill_signal_journal.py tests/test_kill_executor_abort.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_control.py tests/test_control_cli.py tests/test_daemon_tasks.py tests/test_driver.py tests/test_stages.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py tests/test_reconcile.py` exits 0 with every named own-entry Tests obligation, proving the complete cited activation contract and sole-writer record custody through real production composition.
2. `tests/test_kill_cli_activation.py` proves the cited Owner, Records and Observable obligations, calibrated raising worker-boundary dormancy probes, abort and cleanup ordering, truthful kill reporting, identity-bound exactly-once application and terminal-or-restart-reconcilable custody; predecessor assertions migrate only as governed by the own-entry unit.
3. `uv run pytest -q` exits 0 with no test removed or skipped, preservation suites unchanged, and no worker or serve activation.

## Verification
```
uv run pytest tests/test_kill_cli_activation.py tests/test_kill_signal_journal.py tests/test_kill_executor_abort.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_control.py tests/test_control_cli.py tests/test_daemon_tasks.py tests/test_driver.py tests/test_stages.py tests/test_cli.py tests/test_drain.py tests/test_daemon_composition.py tests/test_reconcile.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or contradictory own-entry fact for section 11.4 hardening if the complete contract cannot be met within the earned fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
