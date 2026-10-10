---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- escape-column

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P6
- section 13
- 19.P6.supervised-merge-hold
- 19.P6.go-grade-machinery
- 19.P6.go-grade-run

## Goal / Why
Admit durable supervised daemon merge decisions after escape accounting merges.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML directly from CHUPA_PLAN.md. Position 5 carries admissions[5:]:
- [supervised-merge-hold]
- [go-grade-machinery, go-grade-run]
- [exit-receipt-machinery]
- [phase6-exit]

Author exactly supervised-merge-hold and phase6-continue-06. The payload adds phase6-continue-05 to its registry consumption edge (escape-column); the successor depends on supervised-merge-hold, carries position 6 and admissions[6:], and cites its seeding role plus both GO-grade entries and every entry those seeds require. Admit no later payload now. Refuse forward dependencies; phase6-exit is the sole terminal payload with no successor.

Resolve every role, row and entry citation with resolve_plan_contract before seed writes. Check required_units and entry_unit_gap for payload and successor, including next-admission entries. Inspect Owner, Records, Observable and Tests before grammar and review. Missing or contradictory facts return premise_failed, kind: spec_gap naming the owning unit; never invent a successor contract. Cite ids under Plan contract rather than copying entry prose. Carry every named hold Tests obligation into acceptance; implement none of them in this pass.

Read predecessor owners and merged tests; scan chupa/, eval/ and tests/ for signatures, callers, composition roots, allowlists and negative assertions. Preserve registry names, order, grain and fence floors. Only 19.L rules 2-5 earn additions; record each exact caller or contradicted assertion in tests/test_seeded_phase6_05.py. Read the hold entry's closure requirements, including chupa/daemon.py, chupa/reconcile.py, tests/test_control.py and tests/test_reconcile.py. Other widening requires plan repair. Existing fenced files default to Context; On-demand needs recorded embedding above 300,000 characters. Exclude creations, sibling creations, prompt specs and delimiter-bearing sources. Preservation suites occur only in Verification. Keep historical fixtures unchanged and use merged tests/test_seeded_phase3_core.py as the idiom.

Ordinary rows and continuations start medium/medium. A deep: true row runs alone high/high; supervised-merge-hold is that row. Exits start KNOWN-HARD high/high. Count the successor in seeding.max_seeds_per_admission and cap every stuck budget at drain.max_ticket_minutes.

Snapshot head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin stems/edges, birth, fences, Context partitions, tiers, role citations, position 6, admissions[6:] and named obligations. Compute maximum-effort feasibility from recorded operands only, using the single 400,000-character bound and 0.75 headroom, including the successor. Do not use live-plan/live-size arithmetic or require unbuilt modules.

Write exactly two new seed files directly and leave them uncommitted; commit only tests/test_seeded_phase6_05.py. Check runs requisition_review for each seed and records approvals in tickets/phase6-continue-05/checks.json before one ticket-plane seed lift. On retry retain approved bytes while ticket_sha matches and author only snagged seeds. No Box messages, manual release, production implementation or seeding beyond Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_05.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_05.py` passes with `test_phase6_05_exact_admission` pinning exactly supervised-merge-hold and phase6-continue-06, seed/confirmed birth, registry/seeder edges, role citations, the hold's deep high/high start, the continuation's medium/medium start, batch/stuck bounds, position 6 and admissions[6:].
2. `uv run pytest -q tests/test_seeded_phase6_05.py` passes with `test_phase6_05_entry_depth` checking payload/successor required_units, unique resolution, four depth parts, missing-part rejection, both GO-grade next-admission entries and every named hold Tests obligation.
3. `uv run pytest -q tests/test_seeded_phase6_05.py` passes with `test_phase6_05_closure` pinning earned additions, Context partitions, historical snapshots and fixed maximum-effort feasibility including the successor, without live-plan/live-size arithmetic.
4. `uv run pytest -q tests/test_seeded_phase6_05.py` proves the two seeds remain uncommitted for Check, whose engine-written tickets/phase6-continue-05/checks.json records approvals before a single ticket-plane lift; retry preserves approved bytes while ticket_sha matches.
5. `uv run pytest -q` and all Verification commands pass, preserving merged behavior and immutable historical fixtures.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_05.py
uv run pytest -q tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_restart_timers.py tests/test_baseline.py tests/test_control.py tests/test_control_cli.py tests/test_cli.py tests/test_drain.py tests/test_reconcile.py tests/test_daemon_soak_runner.py
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed with kind: spec_gap naming the owning unit. A criteria-forced path outside earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
