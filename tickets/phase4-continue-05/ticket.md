---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- reliability-run

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- section 13
- 19.P5

## Goal / Why
Check can review and lift the terminal Phase 4 exit seed, completing the finite admission chain.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 from committed CHUPA_PLAN.md. Position 05 carries admissions[5:]: [phase4-exit]. Author only phase4-exit, the sole terminal payload, with no successor. Preserve every registry row and ordering. The exit starts high/high because 19.L names phase exits KNOWN-HARD. Cap this batch at seeding.max_seeds_per_admission and stuck budgets at drain.max_ticket_minutes.

Run resolve_plan_contract for required governing, row and seeder-role citations against the merged plan. Run entry_unit_gap for every required non-exit entry before grammar or review. Missing or contradictory facts return premise_failed, kind: spec_gap, naming the owning cited unit. Cite unit ids; never copy unit text. The exit cites 19.L, 19.I, 19.P4, section 13, 19.P5 and the entry/row citations its next-phase core seeds require. Validate that future entry depth in this owning pass, before writing. Never inspect or seed beyond Phase 5.

The terminal exit realizes all 19.P4 exit reads and the 19.L exit contract. Its dependencies must transitively cover every Phase 4 deliverable, including reliability-run and watchdog-activation. Verify merged presence by reading git squash trailers through git.py, without invented verbs or approval-provenance cross-checks. Read the committed reliability-run report through ReliabilityBatteryReport: classified_quota_exhaustion, all_candidates_cooling_recovery and unclassified_failure_preservation in closed order, all green from member-local production observations and auditor evidence. Preserve machinery/producer separation and engine-lane custody; no hand-committed copy, fixture-written exit evidence or out-of-lane refresh.

Read watchdog-activation's committed passing checks.json for test_production_soft_band_notifies_once_without_kill and test_production_hard_timeout_group_kill_is_harvested. The first proves one soft-band notify intent/completion pair without auto-kill; the second proves hard-timeout group kill and harvested output through production composition. These read obligations name watchdog-detector/watchdog-activation as emitters. Use only committed artifacts or merged wired-and-shaped proofs, never live journal or conditional runtime events. An unmet read returns premise_failed naming it. Name dependency coverage and each read in the exit's acceptance criteria and tests, not a blind suite run.

The exit also authors the 19.P5 core-first admission plus its continuation from the Phase 5 registry, subject to the same seed cap, edges, citation roles, required entry depth and closure laws. Read the next-phase core owners and named tests before authoring, preserve the registry's deep/high starts and avoid forward dependencies. No later admission is authored here.

Read owners, predecessor tickets, direct callers and named tests. Grep signatures, composition sites, allowlists and contradicted/absence assertions across chupa/, eval/ and tests/. Earn additions only under 19.L rules 2-5 or cited seam-owner closure; pin each path's precise reason. Existing fenced paths default to Context; only measured breach of the 300,000-character headroom earns On-demand. Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files never enter Context. Run preservation suites unchanged, neither fenced nor embedded. Historical seeding snapshots remain immutable.

Use merged tests/test_seeded_phase3_core.py as the idiom and create tests/test_seeded_phase4_05.py. Named batch proofs: test_named_stems_cover_exactly_the_terminal_admission, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_exit_cites_next_phase_and_required_core_entries, test_exit_reads_name_emitters_and_cover_transitive_dependencies, test_context_closure_and_max_effort_render_use_authoring_snapshots. Pin exact identity, confirmed birth, grammar, edges, high/high evidence, citation roles, required depth, all exit and core-seeding obligations, earned closure and Context/On-demand partition. Record authoring head, merged idiom blob, file and ticket sizes and cited-unit lengths. Use fixed authoring snapshots for max-effort renders, never live sizes or live plan lengths.

Write the new seed directly and leave it uncommitted; commit only the new batch test. Check owns requisition_review, tickets/phase4-continue-05/checks.json approvals and one ticket-plane seed lift. Keep approved bytes while ticket_sha matches and re-author only snagged seeds. Out: exit implementation, existing tickets/run records, Box messages, manual release, later admissions and plan edits.

## Scope fence
- tickets
- tests/test_seeded_phase4_05.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_05.py` exits 0 proving only the terminal exit with grammar, edges, high/high start, roles, depth, exit reads, core-seeding obligations, closure and fixed renders.
2. `tickets/phase4-continue-05/checks.json` records approvals before Check performs one ticket-plane seed lift; the code commit contains only the batch test.
3. `uv run pytest -q` exits 0 preserving historical snapshots and merged behavior.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_05.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited unit. A criteria-forced path outside the earned fence requires contract repair; never invent facts or change the registry.

## Time budget
- expected: 60m
- stuck: 90m
