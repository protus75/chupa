---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- core-drift-activation
- migrate-config

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P6
- section 13
- 19.P6.host-contract-doc
- 19.P6.fixture-host-scaffold
- 19.P6.core-drift-activation
- section 15
- 19.P6.bug-gate-grammar
- 19.P6.report-inbox-triage
- section 7
- section 12

## Goal / Why
Admit the host documentation and deterministic host fixture after the activated core and config migration.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML in CHUPA_PLAN.md directly; do not copy it into a source file. Position 2 carries admissions[2:]:
- [host-contract-doc, fixture-host-scaffold]
- [bug-gate-grammar, report-inbox-triage]
- [escape-column]
- [supervised-merge-hold]
- [go-grade-machinery, go-grade-run]
- [exit-receipt-machinery]
- [phase6-exit]

Author exactly host-contract-doc, fixture-host-scaffold and phase6-continue-03. Each payload depends on phase6-continue-02 in addition to its registry consumption edges: host-contract-doc consumes migrate-config, and fixture-host-scaffold consumes host-contract-doc and core-drift-activation. The successor depends on both payloads, carries position 3 and admissions[3:], and cites its seeding role, bug-gate-grammar, report-inbox-triage and every entry those seeds require. Admit no later payload now. Refuse forward dependencies; phase6-exit is the sole terminal payload with no successor.

Resolve every role, row and entry citation with resolve_plan_contract before any seed write. Run required_units and entry_unit_gap over all needed non-exit entries, including the successor's next-admission entries. Check Owner, Records, Observable and Tests before grammar or review. A missing or contradictory fact returns premise_failed with kind: spec_gap and the owning unit; never fabricate a successor's governing contract. Cite plan ids under Plan contract rather than copying cited prose. The entry units own the documentation and fixture contracts; carry every named Tests obligation into their acceptance criteria, without implementing either in this admission.

Read the predecessor owners and merged tests first. Scan chupa/, eval/ and tests/ for signatures, direct callers, composition roots, public-operation allowlists and negative assertions under 19.L rules 2-5. Treat each registry fence as its floor and record every earned addition's exact caller or contradicted assertion in tests/test_seeded_phase6_02.py. Any other widening needs plan repair. Existing fenced paths default to Context; use On-demand only when a recorded authoring render exceeds 300,000 characters. Created files, same-admission sibling creations, prompt specs and delimiter-bearing sources are excluded from Context. Preservation suites appear only in Verification. Keep historical seeding fixtures unchanged and use the merged tests/test_seeded_phase3_core.py idiom, never the current admission's test or sibling creation as seed Context.

Ordinary rows and continuations start medium/medium. A deep: true row runs alone at high/high; exits start KNOWN-HARD high/high. Include the successor in the seeding.max_seeds_per_admission batch bound, and constrain every stuck budget to drain.max_ticket_minutes. Keep registry order, names, grain and row coverage unchanged.

Snapshot authoring head, idiom blob, entry hashes, citation lengths, ticket/file bytes and characters, required-unit depth and missing-part rejection in tests/test_seeded_phase6_02.py. Pin grammar, confirmed source: seed birth, exact stems and edges, fence closure, Context partition, tiers, role citations, position and the shrinking suffix. Measure fixed maximum-effort render feasibility solely from those recorded operands using the single 400,000-character bound and 0.75 headroom. Pin successor depth/citations and every payload named obligation without requiring future Phase 6 modules to exist.

Write the three new seed files directly and leave them uncommitted. Commit only tests/test_seeded_phase6_02.py. Check runs requisition_review per seed and records approvals in tickets/phase6-continue-02/checks.json before one ticket-plane seed lift. A retry retains approved bytes while ticket_sha matches and authors only snagged seeds. No Box messages, manual release, production implementation or seeding past Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_02.py` exits 0 with test_phase6_02_exact_admission pinning exactly host-contract-doc, fixture-host-scaffold and phase6-continue-03, confirmed seed birth, registry consumption plus seeder edges, role citations, tiers, bounded batch/stuck budgets, position 3 and admissions[3:].
2. `uv run pytest -q tests/test_seeded_phase6_02.py` exits 0 with test_phase6_02_entry_depth checking payload and successor required_units, unique resolve_plan_contract resolution, all entry_unit_gap parts and missing-part rejection, and carrying every named documentation/fixture Tests obligation.
3. `uv run pytest -q tests/test_seeded_phase6_02.py` exits 0 with test_phase6_02_closure pinning caller/contradiction-earned additions, Context partition, historical snapshots and fixed maximum-effort render feasibility, including the successor, without live-plan or live-size arithmetic.
4. `uv run pytest -q tests/test_seeded_phase6_02.py` exits 0 with exactly the three newly authored seed ticket files left uncommitted for Check; tickets/phase6-continue-02/checks.json is the engine-written approval record before their single ticket-plane lift, retaining approved bytes on retry.
5. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py tests/test_config.py`, `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0, preserving merged behavior and historical snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_02.py
uv run pytest -q tests/test_hostfiles.py tests/test_cli.py tests/test_config.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap naming the owning unit. A forced edit beyond earned closure needs plan repair.

## Time budget
- expected: 60m
- stuck: 90m
