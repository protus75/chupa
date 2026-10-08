---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- storm-producer-wiring
- storm-notification-activation

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.storm-dispatch-hold
- section 12
- section 20
- 19.P3.checkpoint-push
- section 10

## Goal / Why
Advance Phase 3 by exactly one admission: author storm-dispatch-hold and phase3-continue-19 as confirmed seeds, uncommitted for Check to review and lift together.

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md. Read admissions[18:] and each complete needed entry unit, never a copied registry. Run entry_unit_gap and resolve_plan_contract for 19.P3.storm-dispatch-hold and every further next-seeder entry/citation needed from the live registry, resolving row citations and section 13, section 12, section 20 and section 10. The next-seeder lookahead is 19.P3.checkpoint-push and section 10. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only storm-dispatch-hold and phase3-continue-19. The hold depends on phase3-continue-18, starts high/high because its registry row is deep, and cites exactly 19.I, 19.P3.storm-dispatch-hold, section 12 and section 20. Its complete entry unit governs every owner, record shape, sole writer, observable, named invariant test and full Verification command. The renderer injects Owner, Records, Observable and Tests bullets verbatim. Never copy unit text into a seed or into this seeding ticket. Add only seed-specific edges, starts, registry fence floors, earned closure paths and the full entry-unit Verification command. Pin exact own-entry/row citations, named invariant obligations and record custody through governing citations rather than duplicated unit bodies. Carry this cite-don't-copy rule forward to phase3-continue-19.

Read merged chupa/journal.py, chupa/box.py, chupa/config.py, chupa/storm.py, chupa/control.py, chupa/daemon.py, chupa/drain.py, chupa/runner.py, chupa/stages.py, chupa/flake.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before authoring. Preserve the registry floor. Before widening, grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn every caller or predecessor assertion migration under 19.L closure rules 2-5, recording every added path, reason and Context/on-demand partition in this batch's new test. Hold activation must earn every production caller and predecessor dispatch-absence assertion, including tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify, retaining its no-notify proof. Read tests/test_storm.py and tests/test_storm_producer.py for further dispatch-absence assertions; migrate only earned assertions and preserve occurrence, replay, window, corruption, durability and crash obligations. Never migrate historical seeding tests. The hold entry's Records governs record custody and release authority; never derive new records from caller reads.

Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer. Use injected seams, scripted callbacks, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Out: Phase 3 implementation in this batch, replacement writers, task graphs, manual HGATE release, verification filtering and unearned records.

Existing fenced paths are Context by default; On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither, including paths created by a sibling in the same admission. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded.

Create phase3-continue-19 as a medium/medium confirmed source: seed continuation depending on storm-dispatch-hold. Its suffix is admissions[19:], its next payload is checkpoint-push at medium/medium, followed by phase3-continue-20 starting at admissions[20:]. Do not author those later payloads in this batch. Its fence is tickets plus only its own new tests/test_seeded_phase3_19.py. It embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's tests/test_seeded_phase3_18.py. Its Plan contract follows 19.L and section 13's exact seeder roles: 19.L, 19.I, 19.P3, section 13, 19.P3.checkpoint-push, section 10 and every further next-seeder entry/citation needed from the live registry, validated through both operations before writing. Preserve its registry floor and earn caller closure by greps. Carry exact own-entry/row citations, closure greps, named invariant obligations, record custody, Context partition and fixed authoring snapshots forward without copying entry units. 19.P3.checkpoint-push and section 10 are required next-seeder lookahead, not payloads to author here.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix parsed from the plan. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows, or widen a fence without an earned closure path. The suffix is a position in the live registry, never a registry duplicated in a fixture.

Create tests/test_seeded_phase3_18.py naming exactly storm-dispatch-hold and phase3-continue-19. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), seeder/registry edges, starts, exact implementing own-entry/row citations, registry floors and only earned additions with reasons, complete named hold obligations and record custody through exact governing citations, successor exact next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record authoring head, merged idiom blob and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave both new seeds uncommitted for Check to record each requisition_review verdict in tickets/phase3-continue-18/checks.json and lift all approved seeds together through one chupa(phase3-continue-18): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; ticket paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_18.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_18.py` exits 0 over exactly storm-dispatch-hold and phase3-continue-19, proving intake lint, confirmed seed birth, edges, starts and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_18.py` proves exact governing citations without copied unit bodies, earned fences, complete named hold obligations and custody, successor citations/fence/merged idiom, Context closure and max-effort render feasibility from fixed snapshots.
3. At Check, `tickets/phase3-continue-18/checks.json` records requisition_review approve for both seeds, lifted together through one chupa(phase3-continue-18): seeds ticket-plane commit; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_18.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence; never invent records or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
