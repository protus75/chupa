---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- exit-receipt-machinery

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
Admit the terminal Phase 6 exit after its report machinery merges.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P6/END_REGISTRY_P6 YAML directly from CHUPA_PLAN.md. Position 8 carries admissions[8:]:
- [phase6-exit]

Author exactly phase6-exit as the sole terminal payload. Add phase6-continue-08 to its registry depends edges; it consumes exit-receipt-machinery. There is no successor and no seeds authored by phase6-exit. Preserve registry name, order, grain and fence floor. The seeding role cites 19.L, 19.I and 19.P6; the terminal contract is 19.P6's exit reads and RECEIPT together with 19.L's TERMINAL law. Do not invent an exit entry unit or cite an unresolved id.

Before seed writes, resolve role, row and entry ids with resolve_plan_contract. Check required_units and entry_unit_gap for the terminal seed, including every cited non-exit entry and closure through exit-receipt-machinery, fixture-host-scaffold, supervised-merge-hold, go-grade-machinery and go-grade-run. Inspect Owner, Records, Observable and Tests before grammar and review. Missing or contradictory facts return premise_failed, kind: spec_gap naming the owning unit. Cite ids under Plan contract, never copy entry prose. Carry named machinery Tests obligations as unchanged Verification; add named exit tests for each read and transitive dependency coverage.

Read predecessor tickets, owners and merged tests. Scan chupa/, eval/ and tests/ for callers, signatures, composition roots, allowlists and negative assertions. Only 19.L rules 2-5 earn additions; record the exact caller or contradicted assertion in tests/test_seeded_phase6_08.py. Other widening requires plan repair. Existing fenced files default to Context; On-demand requires recorded embedding above 300,000 characters. Exclude creations, prompt specs and delimiter-bearing sources from Context. Unchanged preservation suites occur only in Verification. Keep historical fixtures immutable and use merged tests/test_seeded_phase3_core.py as the idiom.

The exit is KNOWN-HARD and starts high/high, with citing evidence in 19.L. Ordinary rows and continuations start medium/medium; a deep: true row rides alone high/high. Count the sole seed against seeding.max_seeds_per_admission and cap stuck at drain.max_ticket_minutes. Refuse forward dependencies, splitting or bundling.

Snapshot head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin terminal identity/edges, seed/confirmed birth, fence, Context partitions, high/high, role citations, position 8 and admissions[8:] and every exit read with its emitter. Pin transitive coverage of all prior Phase 6 payloads from committed tickets and squash trailers, never live state. Compute maximum-effort feasibility from recorded operands only with the single 400,000-character bound and 0.75 headroom. Do not use live-plan/live-size arithmetic or require unbuilt modules.

The terminal seed's harness command is governed by the machinery entry. Check regenerates its reports into its OUTBOX after purging registered outputs; the existing schema-validating lane lifts them. The receipt reads the committed go-grade-run baseline and actual verdict identity; complete and partial NO_GO are valid evidence. Name machinery and producer for each report/read. Never fabricate report bytes, journal identity or approval provenance. The exit performs no live journal read, authors no next phase, records no GO, and leaves reports uncommitted for Check.

Write exactly one new seed file directly and leave it uncommitted; commit only tests/test_seeded_phase6_08.py. Check runs requisition_review for the seed and records approvals in tickets/phase6-continue-08/checks.json before one ticket-plane seed lift. On retry retain approved bytes while ticket_sha matches and author only snagged seeds. No Box messages, manual release, production implementation or seeding beyond Phase 6.

## Scope fence
- tickets
- tests/test_seeded_phase6_08.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase6_08.py` passes with test_phase6_08_exact_admission pinning exactly phase6-exit, seed/confirmed birth, registry/seeder edges, terminal role citations, KNOWN-HARD high/high, batch/stuck limits, position 8 and admissions[8:]; no successor or terminal seeds.
2. `uv run pytest -q tests/test_seeded_phase6_08.py` passes with test_phase6_08_entry_depth covering required_units, unique resolution, all four depth parts, missing-part rejection and committed terminal read closure through every cited predecessor entry.
3. `uv run pytest -q tests/test_seeded_phase6_08.py` passes with test_phase6_08_closure pinning earned additions, Context partitions, historical snapshots and fixed maximum-effort render operands. The exit acceptance names transitive Phase 6 coverage and each machine_ticket_merge, report_to_regression_bug_loop, escape_attribution and go_grade_report read with its emitter and canonical output.
4. `uv run pytest -q tests/test_seeded_phase6_08.py` proves uncommitted seed custody, individual requisition_review, engine-written tickets/phase6-continue-08/checks.json approvals before one ticket-plane lift and retry preservation of approved bytes while ticket_sha matches.
5. `uv run pytest -q` and all Verification commands pass with immutable historical fixtures.

## Verification
```
uv run pytest -q tests/test_seeded_phase6_08.py
uv run pytest -q tests/test_stages.py tests/test_merge.py tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed with kind: spec_gap naming the owning unit. A criteria-forced file beyond earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
