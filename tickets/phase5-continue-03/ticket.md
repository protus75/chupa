---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- scorecard-reporting

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P5
- 19.P5.status-projection
- 19.P5.baseline-binding-reader
- section 13
- section 12

## Goal / Why
Check admits the next two Phase 5 contracts and one finite continuation.

## Scope in / Scope out
Read committed CHUPA_PLAN.md's BEGIN_REGISTRY_P5/END_REGISTRY_P5 YAML in original order. Position 03 carries admissions[3:]; author exactly status-projection, baseline-binding-reader and phase5-continue-04. Carry position 04 and admissions[4:] into that successor, whose fence is only tickets and tests/test_seeded_phase5_04.py and whose Context embeds merged tests/test_seeded_phase3_core.py. This ticket's batch test is tests/test_seeded_phase5_03.py, never its own Context. Remaining suffix: [status-projection, baseline-binding-reader], [retro-doctor-cli], [phase5-exit]. Do not emit later payloads. The last admission authors only phase5-exit without a successor.

Both row seeds depend on phase5-continue-03 and retain registry consumption edges: status-projection consumes scorecard-reporting and retro-box-activation; baseline-binding-reader consumes retro-box-activation. phase5-continue-04 depends on both status-projection and baseline-binding-reader, consuming every preceding admission payload. No forward dependency. All unmarked rows and continuation seeds start medium/medium; a registry deep: true row starts KNOWN-DEEP high/high on that evidence and occupies its own admission. phase5-exit is KNOWN-HARD high/high under 19.L. Do not invent deep metadata, split rows or reorder admissions.

Before writing any seed, resolve_plan_contract must resolve role, entry and row citations, then required_units and entry_unit_gap must validate every required non-exit entry, including the successor's entries. Read Owner, Records, Observable and Tests. Missing or contradictory facts return premise_failed, kind: spec_gap, naming the owning cited unit. In particular, phase5-continue-04 requires 19.P5.retro-doctor-cli and its row citation; validate that required entry before any file is authored. status-projection cites 19.I, 19.P5.status-projection and section 13; baseline-binding-reader cites 19.I, 19.P5.baseline-binding-reader and section 12. The successor cites 19.L, 19.I, 19.P5, its next admission entry and row citations, plus section 13. Cite identifiers, never copy unit prose or whole section 19. Source new module ownership only from the owning entry.

Retain each next-entry named obligation: test_status_entry_unit, test_status_current_window_scorecard, test_status_production_provenance, test_status_preserves_sections_and_is_write_free, test_status_surfaces_confirmed_class_tombstones, test_status_on_an_empty_journal, test_status_projects_the_journal, test_status_is_deterministic, test_baseline_entry_unit, test_baseline_states_and_latest_signal, test_baseline_routing_and_spec_drift, test_baseline_invalid_inputs_fail_closed, test_author_uses_baseline_resolution, test_bootstrap_without_a_go_or_with_phase_one_no_go_drafts_every_row, test_standing_go_uses_the_table_and_each_override_drafts, test_reopened_retro_ticket_starts_draft. New tests require creation in their entry's test owner, never future Context. Each row's entry test covers required_units, resolve_plan_contract and entry_unit_gap; test_plan_lint stays green. Migrate only caller or contradicted assertions the cited contract forces. Preserve scorecard and retro evidence and assertions; leave retro/doctor verbs and the phase exit to later rows.

Apply 19.L rules 2-5 after reading predecessor owners and scanning signatures, callers, compositions, operation allowlists and negative assertions across chupa/, eval/ and tests/. For the baseline row, scan every go_binds reader/import and retain the eval baseline-identity producer; migrate the interim reader in place without a compatibility path. For status, inspect real CLI projection/provenance and all prior wording assertions. The registry fence is a floor; pin each mechanically earned addition with its precise cause. If criteria force paths beyond earned closure, stop for contract repair. Existing fenced paths default to Context; move one to On-demand only with measured overflow of 300,000 characters. Created paths, same-admission sibling creations, prompt specs and delimiter-bearing sources stay outside Context. Unchanged preservation suites belong in Verification alone.

Pin exactly three seeds, grammar, confirmed source: seed birth, edges, role citations, required entry depths, named obligations, tier evidence, earned closure, shrinking suffix, caps and budgets in tests/test_seeded_phase5_03.py. Record authoring head, merged idiom blob, entry hashes, cited-unit lengths, and file/ticket bytes and characters. Maximum-effort render arithmetic uses fixed authoring snapshots, never live sizes or live plan lengths; historical fixtures remain immutable. Bound every admission, including its successor, by seeding.max_seeds_per_admission; bound each stuck budget by drain.max_ticket_minutes.

Write new seeds directly and leave them uncommitted; only the new batch test is committed on the code branch. Check performs requisition_review, records approvals in tickets/phase5-continue-03/checks.json before a single ticket-plane seed lift. Retain approved bytes while ticket_sha matches; re-author only snagged seeds. No production edits, old tickets/run records, plan edits, Box messages, manual release or extra payloads.

## Scope fence
- tickets
- tests/test_seeded_phase5_03.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase5_03.py` exits 0 proving exactly status-projection, baseline-binding-reader and phase5-continue-04, their birth, grammar, citations, edges, required depths, closure, named obligations, finite suffix and fixed maximum-effort renders.
2. `tickets/phase5-continue-03/checks.json` records requisition_review approvals before one seed lift; only the batch test is committed on the code branch.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving predecessor behavior and immutable historical snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase5_03.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed, kind: spec_gap naming the owning cited unit, before seed creation. A criteria-forced path outside earned closure requires contract repair.

## Time budget
- expected: 60m
- stuck: 180m
