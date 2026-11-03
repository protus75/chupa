---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: human
state: confirmed
---

## Depends on
- phase6-exit

## Context
- tests/test_seeded_phase6_01.py

## Plan contract
- 19.L
- 19.I
- 19.P7
- section 13
- 19.P7.review-spec-readonly
- 19.P7.implement-consumer-read
- section 8
- 19.P7.host-mechanical-check
- section 7

## Goal / Why
Kick off Phase 7 as the first post-bootstrap phase (19.L POST-BOOTSTRAP PHASES): author the 19.P7 core admission and its continuation seeder, so the drain carries Phase 7 and its exit seeds Phase 8.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P7/END_REGISTRY_P7 YAML directly from the plan; never copy it into a source file. This kickoff plays an exit's seeding role at position 0 and carries admissions[0:]:
- [review-spec-readonly, implement-consumer-read]
- [host-mechanical-check]
- [host-review-surfaces]
- [phase7-exit]

Author exactly review-spec-readonly, implement-consumer-read and phase7-continue. Both payloads depend on phase7-core. The successor depends on both payloads and carries position 1 and admissions[1:]; it cites its seeding role, host-mechanical-check, plus every entry its next admission needs. Admit no later payload now and refuse forward edges. Terminal phase7-exit is the sole final payload and has no successor in Phase 7; it authors the 19.P8 core.

Before writing any seed, use resolve_plan_contract to resolve every role, row and entry citation. Run required_units and entry_unit_gap over every needed non-exit entry, including the successor's next-admission entry. Check Owner, Records, Observable and Tests before grammar or review. Missing or contradictory governing facts return premise_failed with kind: spec_gap and the owning cited unit. Cite only ids in Plan contract; copy no cited prose into ticket bodies.

Start ordinary rows and continuations medium/medium; deep: true rows run alone at high/high and exits are KNOWN-HARD high/high. Bound the whole batch including successor by seeding.max_seeds_per_admission, and every stuck budget by drain.max_ticket_minutes. Do not reorder, split, rename, omit or widen a registry row without a plan repair.

Read the merged spec loader and spec tests before authoring. Apply 19.L rules 2-5 across chupa/, eval/ and tests/. Each row fence is the floor; record each earned addition's exact caller or contradicted assertion in tests/test_seeded_phase7_core.py. Existing fenced files default to Context; prompt-spec sources are never Context.

In tests/test_seeded_phase7_core.py snapshot authoring head, idiom blob, entry hashes, citation lengths, file/ticket bytes and characters, required-unit depth and missing-part rejection. Pin grammar, confirmed source: seed birth, exact stems, edges, fence closure, tiers, role citations, position and shrinking suffix, and render feasibility at fixed maximum effort from recorded operands only.

Write the three new seed files directly and leave them uncommitted. Commit only tests/test_seeded_phase7_core.py. Check runs requisition_review per seed and records approvals in tickets/phase7-core/checks.json before one ticket-plane seed lift. No Box messages, manual release, production implementation, or seeding past the first admission.

## Scope fence
- tickets
- tests/test_seeded_phase7_core.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase7_core.py` exits 0 with test_phase7_core_exact_admission pinning precisely review-spec-readonly, implement-consumer-read and phase7-continue, confirmed seed birth, dependency edges, role citations, tiers, position 1 and admissions[1:], bounded batch and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase7_core.py` exits 0 with test_phase7_core_entry_depth checking payload and successor required_units, unique resolve_plan_contract resolution, entry_unit_gap parts and missing-part rejection, and carrying every named Tests obligation of both payload entries.
3. `uv run pytest -q tests/test_seeded_phase7_core.py` exits 0 with exactly the three new seed files uncommitted for Check; tickets/phase7-core/checks.json records each requisition_review approval before their single ticket-plane lift.
4. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving immutable historical seeding snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase7_core.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Any missing or conflicting governing fact returns premise_failed, kind: spec_gap naming its cited unit. A required edit beyond earned closure needs contract repair; no fabricated contract or later payload admission.

## Time budget
- expected: 60m
- stuck: 90m
