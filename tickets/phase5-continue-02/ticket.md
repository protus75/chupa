---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- retro-box-activation

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P5
- 19.P5.scorecard-reporting
- section 14
- section 13

## Goal / Why
Check admits the scorecard machinery and one finite Phase 5 continuation.

## Scope in / Scope out
Read committed CHUPA_PLAN.md's BEGIN_REGISTRY_P5/END_REGISTRY_P5 YAML in its original order. Position 02 carries admissions[2:]; author only scorecard-reporting plus phase5-continue-03. Remaining admissions:
- scorecard-reporting
- status-projection, baseline-binding-reader
- retro-doctor-cli
- phase5-exit

scorecard-reporting depends on phase5-continue-02; phase5-continue-03 depends only on scorecard-reporting. Retain any registry consumption edges; no forward dependency. Carry position 03 and admissions[3:] into the next seeder, whose fence is only tickets and tests/test_seeded_phase5_03.py. It starts medium/medium and embeds the merged earlier tests/test_seeded_phase3_core.py idiom. The scorecard row starts medium/medium; later deep rows start high/high on registry evidence, and the phase exit is KNOWN-HARD high/high under 19.L. Each continuation consumes every preceding admission payload; the last admission authors only phase5-exit without a successor. Do not emit later rows or anything past this phase.

Before either file is written, resolve_plan_contract must resolve the role, entry and row citations, then required_units and entry_unit_gap must validate every required non-exit entry, including the next seeder's entries. Read Owner, Records, Observable and Tests for each. A missing or conflicting fact returns premise_failed with kind: spec_gap and the owning cited unit. Cite identifiers without copying unit prose; never cite whole section 19. The row seed cites 19.I, 19.P5.scorecard-reporting and section 14; the new seeder cites 19.L, 19.I, 19.P5, both next admission entries and their row citations plus section 13. No invented ownership: chupa/scorecard.py belongs to its cited entry. Keep every named obligation, including test_scorecard_entry_unit, test_scorecard_uses_completed_check_evidence, test_scorecard_catches_resolved_and_upheld_findings, test_scorecard_rates_and_prune_threshold, test_scorecard_totals_and_rendering, test_plan_lint, required_units, resolve_plan_contract and entry_unit_gap. New test names require creation, not future Context. Keep tests/test_retro.py assertions unchanged; scorecard test additions belong in tests/test_scorecard.py. Leave later status and baseline behavior to their rows.

Apply 19.L rules 2-5 by reading predecessor owners and scanning signatures, callers, compositions, allowlists and negative assertions throughout chupa/, eval/ and tests/. The registry fence is a floor; pin every earned addition with a precise reason, and put unchanged preservation suites in Verification alone. Pin exactly two seeds, grammar, confirmed source: seed birth, citations and edges, required depths, named obligations, tier evidence, suffix, cap and budgets in tests/test_seeded_phase5_02.py. Record authoring head, merged idiom blob, entry hashes, cited-unit lengths, file/ticket bytes and characters. Use fixed authoring snapshots for maximum-effort renders, never live sizes or plan lengths; historical snapshots remain immutable. Existing fenced paths default to Context; On-demand is earned only by measured overflow of 300,000 characters. Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files stay outside Context.

Write the two new seeds directly, leave them uncommitted and commit only the batch test. Check performs requisition_review, records approvals in tickets/phase5-continue-02/checks.json and performs a single ticket-plane seed lift. Retain approved bytes while ticket_sha matches; re-author only snagged seeds. Bound the batch by seeding.max_seeds_per_admission and each stuck budget by drain.max_ticket_minutes. No production edits, old tickets/run records, plan edits, Box messages, manual release or extra payloads.


## Scope fence
- tickets
- tests/test_seeded_phase5_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase5_02.py` exits 0 proving exactly scorecard-reporting and phase5-continue-03 with confirmed birth, grammar, role citations, consumption edges, required depths, earned closure and fixed maximum-effort renders.
2. `tickets/phase5-continue-02/checks.json` contains Check requisition_review approvals before one seed lift; only the new batch test is committed on the code branch.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged behavior and historical snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase5_02.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap naming the owning cited unit. A criteria-forced path outside earned closure requires contract repair rather than speculative widening.

## Time budget
- expected: 60m
- stuck: 180m
