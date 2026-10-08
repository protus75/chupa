---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- watchdog-event-stream
- notify-transport

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- 19.P4.watchdog-detector
- 19.P4.watchdog-activation
- 19.P4.watchdog-event-stream
- 19.P4.notify-transport
- section 9
- section 13

## Goal / Why
Author Phase 4's second admission and its one successor for Check to review and lift.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 directly from the committed CHUPA_PLAN.md when this ticket runs. Position 01 begins admissions[1:]: [watchdog-detector, watchdog-activation], [provider-cooldown-failover], [reliability-battery], [reliability-run], [phase4-exit]. Author only the first of that shrinking suffix and phase4-continue-02. The successor carries admissions[2:] and depends on both newly authored payloads. Do not rename, reorder, split, omit or add a row, and never author a later admission here. Ordinary seeds start medium/medium; a later deep row or terminal starts high/high only on 19.L's evidence. Bound each stuck budget by drain.max_ticket_minutes and the batch by seeding.max_seeds_per_admission.

Before authoring, validate the needed non-exit entries 19.P4.watchdog-detector and 19.P4.watchdog-activation with entry_unit_gap, and resolve_plan_contract for those entries, their row citations and all needed seeder-role contracts. Revalidate these cited contracts against the merged plan when this continuation runs; uncited later admissions are checked only by their owning pass. A missing or contradictory governing fact returns premise_failed, kind: spec_gap, identifying its owning 19.P4 entry for section 11.4; never supply invented facts or copy plan text. Each implementation seed cites 19.I, its own entry and row citations. Both payloads also cite the event-stream and notify-transport entries they consume; activation additionally cites the detector entry. The successor cites 19.L, 19.I, 19.P4, section 13 and every entry and row contract needed for its next-admission authoring role. A required unit that does not resolve stops that pass as spec_gap; never omit its citation. Required future units are validated at the pass that authors their payloads, not preemptively by an earlier batch.

Both payloads depend on phase4-continue; watchdog-activation also depends on watchdog-detector. The activation must carry every predecessor fixture whose dormancy or negative assertion its behavior invalidates, with the real production-composition proof required by 19.I. Read all row owners, predecessor tickets, direct callers and named tests, and grep public signatures, composition sites, allowlists and absence assertions across chupa/, eval/ and tests/. Earn fence additions only under 19.L rules 2-5 or cited seam-owner closure and pin exact path-specific reasons in the new batch test. Existing fenced paths are embedded unless their measured render exceeds headroom. Created paths, same-admission siblings, prompt specs and delimiter-bearing files never enter Context. Preserve merged serve partitioning and historical seeding snapshots; unchanged preservation suites go only in Verification.

Use the merged tests/test_seeded_phase3_core.py idiom. Create tests/test_seeded_phase4_01.py pinning the exact batch, confirmed seed birth, intake grammar, edges, citation roles, earned fences, named obligations and Context/On-demand partition. Record authoring head, idiom blob, ticket/file sizes and cited-unit lengths in that test, with max-effort base renders bounded by 300,000 characters. Its render arithmetic uses fixed authoring snapshots, never current sizes or current plan lengths. Named tests are test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom and test_context_closure_and_max_effort_render_use_authoring_snapshots.

Write new seeds directly and leave them uncommitted. Check owns requisition_review, tickets/phase4-continue/checks.json approvals and one ticket-plane seed lift. Keep an approved seed verbatim while its bytes match ticket_sha; re-author only snagged seeds. Commit only the new batch test. Out: production implementation, existing tickets/run records, plan edits, Box messages, manual release, later batches and edits to historical tests.

## Scope fence
- tickets
- tests/test_seeded_phase4_01.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_01.py` exits 0 proving precisely watchdog-detector, watchdog-activation and phase4-continue-02 with confirmed birth, grammar, consumption edges and bounded budgets.
2. `uv run pytest -q tests/test_seeded_phase4_01.py` exits 0 proving needed entry depth, citation roles, named obligations, earned closure and fixed-snapshot render feasibility.
3. `tickets/phase4-continue/checks.json` records requisition_review approve for each seed before one ticket-plane seed lift; no seed enters the code commit.
4. `uv run pytest -q` exits 0 preserving merged behavior and historical seeding tests.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_01.py
uv run pytest -q
```

## Definition of rejected
An absent or contradictory needed contract returns premise_failed, kind: spec_gap, naming its owning 19.P4 entry. A criteria-forced file outside earned closure returns premise_failed. Harden the cited entry or repair the authoring fence; do not manufacture evidence or extend the registry.

## Time budget
- expected: 60m
- stuck: 90m
