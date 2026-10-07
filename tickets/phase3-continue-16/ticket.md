---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- flake-detection
- flake-release

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.journal-roll
- section 6
- 19.P3.storm-ledger
- section 12
- 19.P3.storm-producer-wiring
- 19.P3.storm-notification-activation

## Goal / Why
Advance Phase 3 by exactly one admission: author journal-roll, storm-ledger and phase3-continue-17 as confirmed seeds, uncommitted for Check to review and lift together.

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md. Read admissions[16:] and each complete needed entry unit, never a copied registry. Run entry_unit_gap and resolve_plan_contract for 19.P3.journal-roll, 19.P3.storm-ledger, 19.P3.storm-producer-wiring and 19.P3.storm-notification-activation, resolving their row citations and section 13, section 6 and section 12. Validate every further next-seeder entry/citation needed from the live registry through both operations before carrying its contract. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only journal-roll, storm-ledger and phase3-continue-17. journal-roll and storm-ledger depend on phase3-continue-16, start medium/medium and cite exactly 19.I, their own 19.P3 entry and their row's section 6 or section 12 respectively. storm-ledger also depends on journal-roll per its row. Their complete entry units govern every owner, record shape, sole writer, observable, named invariant test and full Verification command. The renderer injects Owner, Records, Observable and Tests bullets verbatim. Never copy unit text into a seed or into this seeding ticket. Add only seed-specific edges, starts, registry fence floors, earned closure paths and the full entry-unit Verification command. Pin exact own-entry/row citations, named invariant obligations and record custody rather than duplicated unit bodies in the seeding test. Carry this cite-don't-copy rule forward to phase3-continue-17.

Read merged chupa/journal.py, chupa/box.py, chupa/config.py, chupa/daemon.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before authoring. Preserve both registry floors. Before widening, grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn any caller or predecessor assertion migration under 19.L closure rules 2-5, recording every added path, reason and Context/on-demand partition in this batch's new test. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable writer; storm ledger remains occurrence-only and dormant, with no trip/report/notification/hold or production hook. Preserve the entry-unit named boundary, replay, corruption, durability and crash obligations. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Out: Phase 3 implementation in this batch, replacement writers, task graphs, production activation, manual HGATE release, verification filtering and unearned records.

Existing fenced paths are Context by default; On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither, including paths created by a sibling in the same admission. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded. Never migrate historical seeding tests.

Create phase3-continue-17 as a medium/medium confirmed source: seed continuation depending on both journal-roll and storm-ledger. Its suffix is admissions[17:], its next payload is storm-producer-wiring and storm-notification-activation, followed by phase3-continue-18 starting at admissions[18:]. Do not author those later payloads in this batch. Its fence is tickets plus only its own new tests/test_seeded_phase3_17.py. It embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's tests/test_seeded_phase3_16.py. Its Plan contract follows 19.L and section 13's exact seeder roles: 19.L, 19.I, 19.P3, section 13, 19.P3.storm-producer-wiring, 19.P3.storm-notification-activation, section 12 and every further next-seeder entry/citation needed from the live registry, validated through both operations before writing. Both storm rows start medium/medium and cite exactly 19.I, their own 19.P3 entry and section 12; storm-notification-activation also depends on storm-producer-wiring per its row. Preserve their registry floors and earn caller closure by greps. Carry exact own-entry/row citations, closure greps, named invariant obligations, record custody, Context partition and fixed authoring snapshots forward without copying entry units. The storm-producer-wiring and storm-notification-activation units and section 12 are required next-seeder lookahead, not payloads to author here. Dormancy and activation migrations must follow each complete unit: the later seeder earns every production caller and predecessor absence assertion path under 19.L rules 2-5.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix parsed from the plan. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows, or widen a fence without an earned closure path. The suffix is a position in the live registry, never a registry duplicated in a fixture.

Create tests/test_seeded_phase3_16.py naming exactly journal-roll, storm-ledger and phase3-continue-17. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), seeder/registry edges, starts, exact implementing own-entry/row citations, registry floors and only earned additions with reasons, complete journal/storm obligations and record custody through exact governing citations, successor exact next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record authoring head, merged idiom blob and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave all three new seeds uncommitted for Check to record each requisition_review verdict in tickets/phase3-continue-16/checks.json and lift all approved seeds together through one chupa(phase3-continue-16): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; ticket paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_16.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_16.py` exits 0 over exactly journal-roll, storm-ledger and phase3-continue-17, proving intake lint, confirmed seed birth, edges, starts and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_16.py` proves exact governing citations without copied unit bodies, earned fences, complete named journal/storm obligations and custody, successor citations/fence/merged idiom, Context closure and max-effort render feasibility from fixed snapshots.
3. At Check, `tickets/phase3-continue-16/checks.json` records requisition_review approve for all three seeds, lifted together through one chupa(phase3-continue-16): seeds ticket-plane commit; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_16.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or contradictory entry-unit fact for section 11.4 hardening, or the criteria-forced path that cannot be earned within the fence; never invent a record or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
