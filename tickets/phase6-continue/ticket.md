---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- core-renderer
- core-drift-classifier

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P6
- section 13
- 19.P6.core-drift-activation
- 19.P6.core-renderer
- 19.P6.core-drift-classifier
- section 7
- section 8
- 19.P6.migrate-config
- section 15
- 19.P6.host-contract-doc
- 19.P6.fixture-host-scaffold

## Goal / Why
Admit the production core gate and config migration after the merged renderer and classifier, keeping the Phase 6 drain's finite seeding chain running.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML directly from the plan; never copy it into a source file. Position 1 carries admissions[1:]:
- [core-drift-activation, migrate-config]
- [host-contract-doc, fixture-host-scaffold]
- [bug-gate-grammar, report-inbox-triage]
- [escape-column]
- [supervised-merge-hold]
- [go-grade-machinery, go-grade-run]
- [exit-receipt-machinery]
- [phase6-exit]

Author exactly core-drift-activation, migrate-config and phase6-continue-02. Both payloads depend on phase6-continue and retain their registry consumption edges; activation consumes core-drift-classifier, and migration consumes core-renderer. The successor depends on both payloads and carries position 2 and admissions[2:]. It cites its seeding role, host-contract-doc and fixture-host-scaffold, plus every entry those payloads need, including core-drift-activation. Admit no later payload now and refuse forward edges. Terminal phase6-exit is the sole final payload and has no successor.

Before writing any seed, use resolve_plan_contract to resolve every role, row and entry citation. Run required_units and entry_unit_gap over every needed non-exit entry, including the successor's next-admission entries. Check Owner, Records, Observable and Tests before grammar or review. Do not fabricate a missing successor entry: missing or contradictory governing facts return premise_failed with kind: spec_gap and the owning cited unit. Cite only ids in Plan contract; copy no cited prose into ticket bodies. The cited activation and migration entries supply their full behavior and named Tests obligations; carry each obligation by name into its seed's acceptance criteria. No owner or contract is invented here.

Activation alone replaces the classifier's production-gate dormancy test and owns the shared chupa/providers.py resolver. Fence the renderer/classifier predecessor fixtures and preserve marker refusal, first adoption, exact project-byte retention, branch-template authority and idempotence. Use the existing core_drift vocabulary; the new caller and merge rerun activate it. Migration owns its CLI registration and config writer through the existing seams, preserving the strict loader's version-zero refusal while making its named repair executable. Author their entry contracts without implementing either in this admission.

Start ordinary rows and continuations medium/medium; deep: true rows run alone at high/high and exits are KNOWN-HARD high/high. Bound the whole batch including successor by seeding.max_seeds_per_admission, and every stuck budget by drain.max_ticket_minutes. Do not reorder, split, rename, omit or widen a registry row without a plan repair.

Read predecessor owners and merged tests before authoring. Apply 19.L rules 2-5 by scanning signatures, direct callers, compositions, public-operation allowlists and negative assertions across chupa/, eval/ and tests/. Each row fence is the floor; record each earned addition's exact caller or contradicted assertion in tests/test_seeded_phase6_01.py. A forced edit with no earned closure needs contract repair. Existing fenced files default to Context; On-demand requires a recorded authoring render exceeding 300,000 characters. Exclude created paths, same-admission sibling creations, prompt specs and delimiter-bearing sources. Preservation suites appear only in Verification. Historical seeding fixtures stay unchanged; use the merged Context idiom, never tests/test_seeded_phase6_01.py or a sibling creation as seed Context.

In tests/test_seeded_phase6_01.py snapshot authoring head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin grammar, confirmed source: seed birth, exact stems, edges, fence closure, tiers, role citations, position and shrinking suffix. Render feasibility at fixed maximum effort reads only those recorded operands, with the single 400,000-character bound and 0.75 authoring headroom. Pin successor citations and depth as well as the payloads' named test obligations. Do not require future Phase 6 modules to exist in this seeding proof.

Write the three new seed files directly and leave them uncommitted. Commit only tests/test_seeded_phase6_01.py. Check runs requisition_review per seed and records approvals in tickets/phase6-continue/checks.json before one ticket-plane seed lift. A retry retains approved bytes while ticket_sha matches and authors only snagged seeds. No Box messages, manual release, production implementation, or seeding past Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_01.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_01.py` exits 0 with test_phase6_01_exact_admission pinning precisely core-drift-activation, migrate-config and phase6-continue-02, confirmed seed birth, dependency consumption, role citations, tiers, position 2 and admissions[2:], bounded batch and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase6_01.py` exits 0 with test_phase6_01_entry_depth checking payload and successor required_units, unique resolve_plan_contract resolution, entry_unit_gap parts and missing-part rejection, and carrying every named activation/migration Tests obligation.
3. `uv run pytest -q tests/test_seeded_phase6_01.py` exits 0 with test_phase6_01_closure pinning the activation's predecessor dormancy transition, caller/contradiction-earned additions, Context partition and historical operands for fixed maximum-effort render feasibility.
4. `uv run pytest -q tests/test_seeded_phase6_01.py` exits 0 with exactly the three new seed files uncommitted for Check; tickets/phase6-continue/checks.json records each requisition_review approval before their single ticket-plane lift.
5. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py`, `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving the merged core and immutable historical snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_01.py
uv run pytest -q tests/test_hostfiles.py tests/test_cli.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Any missing or conflicting governing fact returns premise_failed, kind: spec_gap naming its cited unit. A required edit beyond earned closure needs contract repair; no fabricated contract or later payload admission.

## Time budget
- expected: 60m
- stuck: 90m
