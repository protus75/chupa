---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- watchdog-detector
- watchdog-activation

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- 19.P4.provider-cooldown-failover
- 19.P3.thresh-runtime
- section 6
- section 15
- section 13

## Goal / Why
Author the deep provider admission and its successor for Check to review and lift.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 directly from committed CHUPA_PLAN.md. Position 02 carries admissions[2:]: [provider-cooldown-failover], [reliability-battery], [reliability-run], [phase4-exit]. Author only provider-cooldown-failover and phase4-continue-03. The successor carries admissions[3:] and depends on the payload; the payload depends on phase4-continue-02. Never rename, reorder, split, omit or add a row or author a later admission. This deep payload starts high/high on 19.L's known-deep evidence; the successor starts medium/medium. Bound each stuck budget by drain.max_ticket_minutes and the batch by seeding.max_seeds_per_admission.

Before authoring, run entry_unit_gap on 19.P4.provider-cooldown-failover and the required 19.P3.thresh-runtime. Run resolve_plan_contract for each needed entry, row citation and seeder-role contract against the merged plan. Missing or contradictory facts return premise_failed, kind: spec_gap, naming the owning entry; never invent facts or copy plan prose. The payload cites 19.I, its own entry, sections 6 and 15 and 19.P3.thresh-runtime as required by its Owner. The successor cites 19.L, 19.I, 19.P4, section 13 and every entry/row citation needed to author its next admission. Required future citation resolution cannot be omitted; future payload entry depth is validated by its owning pass, not preemptively for uncited later admissions.

Read row owners, predecessor tickets, direct callers and named tests. Grep public signatures, constructor/composition sites, allowlists and absence assertions across chupa/, eval/ and tests/. Earn additions only under 19.L rules 2-5 or cited seam-owner closure and pin exact path-specific reasons. Carry classifier/threshold predecessor dormancy fixtures, including tests/test_thresh.py, while preserving merged watchdog and serve behavior. Embed existing fenced paths unless measured headroom forces On-demand. Created paths, same-admission siblings, prompt specs and delimiter-bearing files never enter Context. Unchanged preservation suites belong only in Verification; historical seeding snapshots are immutable.

Use merged tests/test_seeded_phase3_core.py as the idiom. Create tests/test_seeded_phase4_02.py pinning the exact admission/successor, confirmed birth, intake grammar, edges, citation roles, needed entry depth, named obligations, earned fences and Context/On-demand partition. Record authoring head, idiom blob, ticket/file sizes and cited-unit lengths; max-effort base renders fit 300,000 characters using fixed authoring snapshots, never current sizes or plan lengths. Named tests: test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom and test_context_closure_and_max_effort_render_use_authoring_snapshots.

Write new seeds directly and leave them uncommitted. Check owns requisition_review, this seeder's checks.json approvals and one ticket-plane seed lift. Keep approved bytes verbatim while ticket_sha matches; re-author only snagged seeds. Commit only the new batch test. Out: production implementation, existing tickets/run records, plan edits, Box messages, manual release, later admissions and historical test edits.

## Scope fence
- tickets
- tests/test_seeded_phase4_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_02.py` exits 0 proving exactly provider-cooldown-failover and phase4-continue-03, confirmed births, grammar, edges, bounded budgets, citation roles, entry depth, named obligations, earned closure and fixed-snapshot renders.
2. `tickets/phase4-continue-02/checks.json` records each approval before one ticket-plane seed lift; the code commit contains only the new batch test.
3. `uv run pytest -q` exits 0 preserving merged behavior and historical seeding snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_02.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. A criteria-forced path outside the earned fence returns premise_failed; repair the contract or closure rather than invent facts or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m

