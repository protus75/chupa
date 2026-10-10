---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- host-contract-doc
- fixture-host-scaffold

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P6
- section 13
- 19.P6.bug-gate-grammar
- 19.P6.report-inbox-triage
- 19.P6.escape-column

## Goal / Why
Admit regression grammar and durable report intake after the fixture host merges.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML directly from CHUPA_PLAN.md; do not copy it into source. Position 3 carries admissions[3:]:
- [bug-gate-grammar, report-inbox-triage]
- [escape-column]
- [supervised-merge-hold]
- [go-grade-machinery, go-grade-run]
- [exit-receipt-machinery]
- [phase6-exit]

Author exactly bug-gate-grammar, report-inbox-triage and phase6-continue-04. Payloads add phase6-continue-03 to registry consumption edges: bug-gate-grammar consumes fixture-host-scaffold; report-inbox-triage consumes bug-gate-grammar. The successor depends on both payloads, carries position 4 and admissions[4:], and cites its seeding role, escape-column and every entry its escape seed requires. Admit no later payload now. Refuse forward dependencies; phase6-exit is the sole terminal payload with no successor.

Resolve every role, row and entry citation with resolve_plan_contract before seed writes. Check required_units and entry_unit_gap for each payload and successor, including next-admission entries. Inspect Owner, Records, Observable and Tests before grammar and review. Missing or contradictory governing facts return premise_failed, kind: spec_gap naming the owning unit; never fabricate a successor contract. Cite ids under Plan contract instead of copying prose. Carry every named payload Tests obligation into acceptance without implementing it here.

Read predecessor owners and merged tests; scan chupa/, eval/ and tests/ for signature callers, composition roots, public-operation allowlists and negative assertions. Keep registry names, order, grain and floor fences; only 19.L rules 2-5 earn additions, each recorded with exact caller or contradicted assertion in tests/test_seeded_phase6_03.py. Any other widening requires plan repair. Existing fenced files default to Context; On-demand requires a recorded embedding render above 300,000 characters. Exclude created files, sibling creations, prompt specs and delimiter-bearing sources. Preservation suites belong only in Verification. Leave historical fixtures unchanged; use the merged tests/test_seeded_phase3_core.py idiom, never the admission's new test or sibling creation.

Ordinary rows and continuations start medium/medium. A deep: true row runs alone at high/high; exits start KNOWN-HARD high/high. Include the successor in seeding.max_seeds_per_admission and bound every stuck budget by drain.max_ticket_minutes.

Snapshot authoring head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin birth, exact stems/edges, fence closure, Context partitions, tiers, role citations, position 4, admissions[4:] and named obligations. Compute fixed maximum-effort feasibility solely from recorded operands with the single 400,000-character bound and 0.75 headroom; no live-plan or live-size arithmetic or requirement for unbuilt modules.

Write exactly three new seed files directly and leave them uncommitted; commit only tests/test_seeded_phase6_03.py. Check runs requisition_review per seed and records approvals in tickets/phase6-continue-03/checks.json before one ticket-plane seed lift. A retry retains approved bytes while ticket_sha matches and authors only snagged seeds. No Box messages, manual release, production implementation or seeding past Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_03.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_03.py` exits 0 with test_phase6_03_exact_admission pinning exactly bug-gate-grammar, report-inbox-triage and phase6-continue-04, confirmed source: seed birth, registry consumption and seeder edges, role citations, tiers, batch/stuck bounds, position 4 and admissions[4:].
2. `uv run pytest -q tests/test_seeded_phase6_03.py` exits 0 with test_phase6_03_entry_depth checking payload/successor required_units, unique resolution, all four depth parts and missing-part rejection, and every named bug-gate/report-inbox Tests obligation.
3. `uv run pytest -q tests/test_seeded_phase6_03.py` exits 0 with test_phase6_03_closure pinning earned additions, Context partition, historical snapshots and fixed maximum-effort feasibility including the successor without live-plan or live-size arithmetic.
4. `uv run pytest -q tests/test_seeded_phase6_03.py` exits 0 with exactly three new seed files left uncommitted for Check; tickets/phase6-continue-03/checks.json is the engine-written approval record before their single ticket-plane lift, retaining approved bytes on retry.
5. `uv run pytest -q` and the other Verification commands exit 0 preserving merged behavior and immutable historical fixtures.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_03.py
uv run pytest -q tests/test_tickets.py tests/test_gates.py tests/test_box.py tests/test_triage.py tests/test_author.py tests/test_serve.py
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap naming the owning unit. A forced edit beyond earned closure needs plan repair.

## Time budget
- expected: 60m
- stuck: 90m
