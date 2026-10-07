---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-15
- flake-detection

## Context
- chupa/daemon.py
- chupa/box.py
- chupa/journal.py
- chupa/config.py
- chupa/seams.py
- chupa/__main__.py

## Plan contract
- 19.I
- 19.P3.flake-release
- section 11

## Goal / Why
Section 11.5 identity-bound mechanical release.

## Scope in / Scope out
19.P3.flake-release governs this deliverable. chupa/flake.py owns the component; chupa/daemon.py owns its dormant composition hook, using the existing lock holder’s Journal and Box.

Read the merged production code and the real CLI run/drain and build_daemon_core before editing. The cited own entry is the complete governing contract for Owner, Records, Observable and every named Tests obligation: implement all of it, including record custody and its sole writers, through the unit's Owner. The renderer injects these bullets verbatim. Never copy unit text into the ticket.

Preserve callable signatures, bootstrap on-entry reconciliation and inline admission. Production dormancy must use calibrated raising hook probes over real CLI run/drain and the merged production-composition harness: deliberate construction and invocation wiring must trip each assertion. Direct injected invocation exercises the component; serve-activation owns production hook activation and dormancy migration. Reuse the merged CoreRig in tests/test_daemon_composition.py and the disposable CLI fixtures on demand as read-only idioms, never edit them. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits.

Authoring greps across chupa/, eval/ and tests/ covered flake, quarantine, daemon_core, build_daemon_core, Box, Journal, not hasattr, __all__, task counts and serve absence under 19.L rules 2-5. No public signature, constructor arity or composition-root wiring changes, no public-operation allowlist needs migration, and no predecessor production assertion flips: no fence additions are earned. Preserve ordinary DaemonTasks exception propagation and cleanup. Never migrate historical seeding tests. Existing fenced chupa/daemon.py is Context; the flake module and test created in this admission are neither Context nor On-demand, including for the sibling release. All other Context paths are merged read-only references. Keep unfenced suites as unchanged preservation suites in Verification only, neither fenced nor embedded.

Out: continuous production wiring, replacement writers, task graphs, manual HGATE release, actual verification execution/filtering and unearned records.

Preserve detection, dedup and quarantine-cap behavior and keep the complete detection suite green.

## Scope fence
- chupa/flake.py
- chupa/daemon.py
- tests/test_flake.py

## Acceptance criteria

1. `uv run pytest tests/test_flake.py` proves `test_release_construction_is_idle` with the full invariant governed by `19.P3.flake-release`.
2. `uv run pytest tests/test_flake.py` proves `test_release_resolves_exact_box_identity` with the full invariant governed by `19.P3.flake-release`.
3. `uv run pytest tests/test_flake.py` proves `test_release_requires_matching_merge_and_named_green_rerun` with the full invariant governed by `19.P3.flake-release`.
4. `uv run pytest tests/test_flake.py` proves `test_release_signal_is_write_ahead` with the full invariant governed by `19.P3.flake-release`.
5. `uv run pytest tests/test_flake.py` proves `test_release_replay_and_restart` with the full invariant governed by `19.P3.flake-release`.
6. `uv run pytest tests/test_flake.py` proves `test_release_preserves_other_quarantines` with the full invariant governed by `19.P3.flake-release`.
7. `uv run pytest tests/test_flake.py` proves `test_flake_release_is_dormant` with the full invariant governed by `19.P3.flake-release`.
8. `uv run pytest tests/test_flake.py tests/test_box.py tests/test_journal.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py` exits 0 with every preservation suite unchanged; `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_flake.py tests/test_box.py tests/test_journal.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or contradictory entry-unit fact for section 11.4 hardening, or the criteria-forced path that cannot be earned within the fence; never invent a record or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
