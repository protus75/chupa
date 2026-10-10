---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- bug-gate-grammar
- report-inbox-triage

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P6
- section 13
- 19.P6.escape-column
- 19.P6.bug-gate-grammar
- 19.P6.report-inbox-triage
- 19.P6.supervised-merge-hold

## Goal / Why
Admit pure escape accounting after durable report intake merges.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML directly from CHUPA_PLAN.md. Position 4 carries admissions[4:]:
- [escape-column]
- [supervised-merge-hold]
- [go-grade-machinery, go-grade-run]
- [exit-receipt-machinery]
- [phase6-exit]

Author exactly escape-column and phase6-continue-05. The payload adds phase6-continue-04 to its registry consumption edges (bug-gate-grammar and report-inbox-triage); the successor depends on escape-column, carries position 5 and admissions[5:], and cites its seeding role, supervised-merge-hold and every entry its hold seed requires. Admit no later payload now. Refuse forward dependencies; phase6-exit is the sole terminal payload with no successor.

Resolve every role, row and entry citation with resolve_plan_contract before seed writes. Check required_units and entry_unit_gap for payload and successor, including next-admission entries. Inspect Owner, Records, Observable and Tests before grammar and review. Missing or contradictory facts return premise_failed, kind: spec_gap naming the owning unit; never invent a successor contract. Cite ids under Plan contract instead of copying unit prose. Carry every named escape Tests obligation into acceptance; this pass implements none of them.

Read predecessor owners and merged tests; scan chupa/, eval/ and tests/ for signatures, callers, composition roots, allowlists and negative assertions. Keep registry names, order, grain and fence floors. Only 19.L rules 2-5 earn additions; record each exact caller or contradicted assertion in tests/test_seeded_phase6_04.py. The escape entry identifies triage ownership and its closure additions; read that entry before authoring. Other widening needs plan repair. Existing fenced files default to Context; On-demand requires recorded embedding above 300,000 characters. Exclude creations, sibling creations, prompt specs and delimiter-bearing sources. Preservation suites appear only in Verification. Keep historical fixtures unchanged and use merged tests/test_seeded_phase3_core.py as the idiom.

Ordinary rows and continuations start medium/medium. A deep: true row runs alone high/high; exits start KNOWN-HARD high/high. Count the successor in seeding.max_seeds_per_admission and cap each stuck budget at drain.max_ticket_minutes.

Snapshot head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin exact stems/edges, birth, fences, Context partitions, tiers, role citations, position 5, admissions[5:] and named obligations. Compute maximum-effort feasibility solely from recorded operands with the single 400,000-character bound and 0.75 headroom; no live-plan/live-size arithmetic or requirement for unbuilt modules.

Write exactly two new seed files directly and leave them uncommitted; commit only tests/test_seeded_phase6_04.py. Check runs requisition_review for each seed and records approvals in tickets/phase6-continue-04/checks.json before one ticket-plane seed lift. On retry retain approved bytes while ticket_sha matches and author only snagged seeds. No Box messages, manual release, production implementation or seeding beyond Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_04.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_04.py` exits 0 with `test_phase6_04_exact_admission` pinning exactly escape-column and phase6-continue-05, seed/confirmed birth, registry/seeder edges, role citations, tiers, batch/stuck bounds, position 5 and admissions[5:].
2. `uv run pytest -q tests/test_seeded_phase6_04.py` exits 0 with `test_phase6_04_entry_depth` checking payload/successor required_units, unique resolution, four depth parts, missing-part rejection and every named escape Tests obligation.
3. `uv run pytest -q tests/test_seeded_phase6_04.py` exits 0 with `test_phase6_04_closure` pinning earned additions, Context partitions, historical snapshots and fixed maximum-effort feasibility including the successor, without live-plan/live-size arithmetic.
4. `uv run pytest -q tests/test_seeded_phase6_04.py` checks that two seeds remain uncommitted for Check, whose engine-written `tickets/phase6-continue-04/checks.json` records approvals before a single ticket-plane lift and whose retry preserves approved bytes while ticket_sha matches.
5. `uv run pytest -q` and all Verification commands exit 0, preserving merged behavior and immutable historical fixtures.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_04.py
uv run pytest -q tests/test_scorecard.py tests/test_git.py tests/test_triage.py tests/test_retro.py tests/test_cli.py tests/test_mergequeue.py
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing entry facts return premise_failed with kind: spec_gap and the owning unit. A criteria-forced path outside earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
