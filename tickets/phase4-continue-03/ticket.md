---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- provider-cooldown-failover

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- 19.P4.reliability-battery
- 19.P4.provider-cooldown-failover
- 19.P4.reliability-run
- section 6
- section 13

## Goal / Why
Author the closed reliability battery admission and its successor for Check to review and lift.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 from committed CHUPA_PLAN.md. Position 03 carries admissions[3:]: [reliability-battery], [reliability-run], [phase4-exit]. Author exactly reliability-battery and phase4-continue-04; the payload depends on phase4-continue-03 and the successor depends on reliability-battery. The successor carries admissions[4:]. Keep all registry rows and admission order intact. Both new seeds start medium/medium. Cap the batch with seeding.max_seeds_per_admission and each stuck budget with drain.max_ticket_minutes.

Before writing, run entry_unit_gap for 19.P4.reliability-battery and its required cited 19.P4.provider-cooldown-failover. Run resolve_plan_contract for all needed entry units, registry row citations and seeder-role citations against the merged plan, including the required next-successor citation 19.P4.reliability-run. Missing or contradictory facts stop as premise_failed, kind: spec_gap, naming the owning cited entry; do not invent facts. Validate future entry depth in its owning pass, without preemptively inspecting uncited later admissions. Cite plan units rather than copying their prose.

The battery implements its own entry and registry row, citing 19.I, 19.P4.reliability-battery, 19.P4.provider-cooldown-failover and section 6. New eval/reliability_battery.py owns the runner/writer; chupa/artifacts.py owns the closed models and chupa/stages.py owns report registration. It constructs the machinery only; reliability-run later produces the report. The successor cites 19.L, 19.I, 19.P4, section 13 and all entry/row citations its next admission needs. Do not author reliability-run or phase4-exit in this pass.

Read owners, predecessor tickets, direct callers and named tests. Grep signatures, construction sites, public allowlists and contradicted/absence assertions across chupa/, eval/ and tests/. Earn additions only under 19.L rules 2-5 or cited seam-owner closure, recording each path's precise reason. Existing fenced paths default to Context; measured headroom alone moves them On-demand. Created paths, same-admission siblings, prompt specs and delimiter-bearing files never enter Context. Unchanged preservation suites go only in Verification. Keep all historical seeding tests immutable.

Use merged tests/test_seeded_phase3_core.py as the idiom. Create tests/test_seeded_phase4_03.py with test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom and test_context_closure_and_max_effort_render_use_authoring_snapshots. Pin exact identity, confirmed birth, intake grammar, edges, citation roles, required entry depth, every named obligation, earned closure and Context/On-demand partition. Record authoring head, idiom blob, ticket/file sizes and cited-unit lengths. Use fixed authoring snapshots for max-effort base renders under 300,000 characters; never recompute against live sizes or plan lengths.

Write the two seeds directly and leave them uncommitted. Check owns requisition_review, this seeder's checks.json approvals and one ticket-plane seed lift. Preserve approved bytes while ticket_sha matches; re-author only snagged seeds. Commit only the new batch test. Out: implementation, existing tickets or run records, plan edits, Box messages, manual release, later admissions and historical test edits.

## Scope fence
- tickets
- tests/test_seeded_phase4_03.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_03.py` exits 0 proving exactly the battery and successor, grammar, confirmed birth, edges, budgets, citation roles, required entry depth, named obligations, closure and fixed-snapshot renders.
2. `tickets/phase4-continue-03/checks.json` records each approval before one ticket-plane seed lift; the code commit contains only the new batch test.
3. `uv run pytest -q` exits 0 preserving merged behavior and historical seeding snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_03.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. If the criteria require a path outside the earned fence, repair the contract or closure rather than inventing facts or changing the registry.

## Time budget
- expected: 60m
- stuck: 90m
