---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- go-grade-machinery
- go-grade-run

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P6
- section 13
- 19.P6.exit-receipt-machinery
- 19.P6.fixture-host-scaffold
- 19.P6.supervised-merge-hold
- 19.P6.go-grade-machinery
- 19.P6.go-grade-run

## Goal / Why
Admit the supervised fixture loop and receipt machinery after GO-grade evidence merges.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML directly from CHUPA_PLAN.md. Position 7 carries admissions[7:]:
- [exit-receipt-machinery]
- [phase6-exit]

Author exactly exit-receipt-machinery and phase6-continue-08. Add phase6-continue-07 to the machinery's registry edges; it consumes go-grade-run. The successor depends on exit-receipt-machinery, carries position 8 and admissions[8:], and cites its seeding role and the terminal phase6-exit contract. Admit no terminal payload in this pass. Refuse forward dependencies; phase6-exit is the sole terminal payload with no successor and no seeds.

Resolve role, row and entry ids with resolve_plan_contract before seed writes. Check required_units and entry_unit_gap for machinery and successor, including next-admission entries and closure through fixture-host-scaffold, supervised-merge-hold, go-grade-machinery and go-grade-run. Inspect Owner, Records, Observable and Tests before grammar and review. Missing or contradictory facts return premise_failed, kind: spec_gap naming the owning unit; never invent a successor contract. Cite ids under Plan contract rather than copying entry prose. Carry every named machinery Tests obligation into acceptance.

Read predecessor owners and merged tests; scan chupa/, eval/ and tests/ for signatures, callers, composition roots, allowlists and negative assertions. Preserve registry names, order, grain and fence floors. Only 19.L rules 2-5 earn additions; record each exact caller or contradicted assertion in tests/test_seeded_phase6_07.py. Other widening requires plan repair. Existing fenced files default to Context; On-demand needs recorded embedding above 300,000 characters. Exclude creations, sibling creations, prompt specs and delimiter-bearing sources from Context. Preservation suites occur only in Verification. Keep historical fixtures unchanged and use merged tests/test_seeded_phase3_core.py as the idiom.

Ordinary rows and continuations start medium/medium. A deep: true row runs alone high/high. Exits start KNOWN-HARD high/high. Count the successor in seeding.max_seeds_per_admission and cap every stuck budget at drain.max_ticket_minutes. This admission has two seeds including its successor; do not split or bundle rows.

Snapshot head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin stems/edges, birth, fences, Context partitions, tiers, role citations, position 8, admissions[8:] and named obligations. Compute maximum-effort feasibility from recorded operands only, using the single 400,000-character bound and 0.75 headroom, including the successor. Do not use live-plan/live-size arithmetic or require unbuilt modules.

Write exactly two new seed files directly and leave them uncommitted; commit only tests/test_seeded_phase6_07.py. Check runs requisition_review for each seed and records approvals in tickets/phase6-continue-07/checks.json before one ticket-plane seed lift. On retry retain approved bytes while ticket_sha matches and author only snagged seeds. No Box messages, manual release, production implementation or seeding beyond Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_07.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_07.py` passes with test_phase6_07_exact_admission pinning exactly exit-receipt-machinery and phase6-continue-08, seed/confirmed birth, registry/seeder edges, role citations, medium/medium starts, batch/stuck bounds, position 8 and admissions[8:].
2. `uv run pytest -q tests/test_seeded_phase6_07.py` passes with test_phase6_07_entry_depth checking both seeds required_units, unique resolution, four depth parts, missing-part rejection, terminal successor closure and every named machinery Tests obligation.
3. `uv run pytest -q tests/test_seeded_phase6_07.py` passes with test_phase6_07_closure pinning earned additions, Context partitions, historical snapshots and fixed maximum-effort feasibility including the successor without live-plan/live-size arithmetic.
4. `uv run pytest -q tests/test_seeded_phase6_07.py` proves seeds remain uncommitted for Check; engine-written tickets/phase6-continue-07/checks.json records approvals before one ticket-plane lift and retry preserves approved bytes while ticket_sha matches.
5. `uv run pytest -q` and all Verification commands pass, preserving merged behavior and immutable historical fixtures.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_07.py
uv run pytest -q tests/test_stages.py tests/test_merge.py tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing entry facts return premise_failed, kind: spec_gap naming the owning unit. A criteria-forced path beyond earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
