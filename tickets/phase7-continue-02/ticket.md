---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- host-mechanical-check

## Context
- tests/test_seeded_phase6_01.py

## Plan contract
- 19.L
- 19.I
- 19.P7
- section 13
- 19.P7.host-review-surfaces
- section 4
- section 7
- section 9
- section 8

## Goal / Why
Admit the Phase 7 host surface payload and its bounded terminal continuation.

## Scope in / Scope out
This is Position 2, carrying admissions[2:] of the committed Phase 7 registry: host-review-surfaces, then phase7-exit alone. Parse its YAML from the plan; never copy it to a source file. Author exactly host-review-surfaces and phase7-continue-03. The surface payload depends on phase7-continue-02 and host-mechanical-check. The successor depends on host-review-surfaces and carries position 3 and admissions[3:]. Admit no exit payload now and refuse forward edges. Carry the seeding-role citations into that successor, including the next phase unit when its admission authors the exit.

Use medium/medium for continuations and ordinary rows. The deep: true host-review-surfaces row is alone and high/high. The terminal phase7-exit alone is KNOWN-HARD high/high; it has no successor in Phase 7 and authors the 19.P8 core. Count the entire emitted set, successor included, against seeding.max_seeds_per_admission. Bound stuck minutes by drain.max_ticket_minutes. Keep registry row names, order, admission grouping and obligations fixed.

Resolve every role, row citation and required entry before writing a seed. Run required_units and entry_unit_gap for every needed non-exit unit; inspect Owner, Records, Observable and Tests before grammar and review. Missing or conflicting governing facts stop as premise_failed, kind: spec_gap with the owning unit. Keep plan text behind Plan contract ids. Carry all named Tests obligations of the host-review-surfaces entry, including its host-only render, routing fallback, Box publication identity, mechanical/surface bypass separation and both merge admission modes. Read the merged production owners and tests first, then apply 19.L closure rules 2-5 across chupa/, eval/ and tests/. The row fence is a minimum; record each exact caller or contradicted assertion earning an addition. Preserve historical seeding fixtures unchanged.

Embed existing fenced material in Context unless its measured contribution breaches headroom; record bytes and characters for any On-demand move. Prompt specs and delimiter-bearing sources stay outside Context. Future files occur in neither input list. Use a merged earlier seeding test as the successor's idiom, never the new test from this admission. Record authoring head, idiom blob, entry hashes, citation lengths, ticket/file byte and character counts, required-unit depth and missing-part rejection. Pin grammar, seed birth, exact stems, dependencies, tiers, fences, input partition, position and shrinking suffix. Calculate maximum-effort base Implement feasibility solely from recorded operands.

Write only the two new confirmed source: seed files and leave them uncommitted. Commit the admission snapshot test only. Check performs requisition_review separately for each seed, writes per-seed approvals into this ticket's checks.json, and owns the single ticket-plane seed lift. Keep approved bytes while ticket_sha matches and re-author only snagged seeds. Implement performs no reviews, approval writes, manual release or lift. Do not file Box messages, implement production behavior or seed beyond this admission.

## Scope fence
- tickets
- tests/test_seeded_phase7_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase7_02.py` exits 0 with test_phase7_02_exact_admission asserting the two required stems, confirmed seed birth, row/seeder edges, roles, high/high surface payload, medium/medium successor, position 3 and admissions[3:], admission cap, stuck ceiling and no future dependency.
2. `uv run pytest -q tests/test_seeded_phase7_02.py` exits 0 with test_phase7_02_entry_depth recording required_units, unique resolve_plan_contract results and every entry_unit_gap part with missing-part rejection for all non-exit units needed by either seed. The surface payload names every test from its entry.
3. `uv run pytest -q tests/test_seeded_phase7_02.py` exits 0 with test_phase7_02_closure and test_phase7_02_render pinning forced fence additions, input partition and recorded sizes, entry hashes, citation lengths and maximum-effort render arithmetic from saved operands. Leave both seed files uncommitted for Check's individual requisition_review approvals in checks.json and single ticket-plane seed lift.
4. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0; no historical seeding fixture changes.

## Verification
```
uv run pytest -q tests/test_seeded_phase7_02.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A governing gap stops with premise_failed and its owning entry unit. A forced edit outside the earned fence requires contract repair.

## Time budget
- expected: 60m
- stuck: 90m
