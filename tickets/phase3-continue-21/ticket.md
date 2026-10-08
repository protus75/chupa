---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- serve-activation

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.serve-merge-admission
- section 9
- 19.P3.worker-recovery-disposition
- section 6
- section 15

## Goal / Why
Advance Phase 3 by exactly one admission: author serve-merge-admission and phase3-continue-22 as confirmed seeds, uncommitted for Check to review and lift together.

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md. Read admissions[21:] and every complete needed entry unit, never a copied registry. Run entry_unit_gap and resolve_plan_contract for 19.P3.serve-merge-admission and every further next-seeder entry/citation needed from the live registry, resolving row citations and section 13, section 9, section 6 and section 15. The next-seeder lookahead is 19.P3.worker-recovery-disposition with section 6 and section 15. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only serve-merge-admission and phase3-continue-22. serve-merge-admission depends on phase3-continue-21, starts high/high because its registry row is deep, and cites exactly 19.I, 19.P3.serve-merge-admission and section 9. Its complete entry unit governs every owner, record shape, sole writer, observable, named invariant test and full Verification command. The renderer injects Owner, Records, Observable and Tests bullets verbatim. Never copy unit text into a seed or into this seeding ticket. Add only seed-specific edges, starts, registry fence floors, earned closure paths and the full entry-unit Verification command. Pin exact own-entry/row citations, every named invariant obligation and record custody through governing citations rather than duplicated unit bodies. Carry this cite-don't-copy rule forward to phase3-continue-22.

Read merged chupa/merge.py, chupa/serve.py, chupa/runner.py, chupa/daemon.py, chupa/stages.py, chupa/mergequeue.py, chupa/__main__.py, chupa/control.py, chupa/drain.py, chupa/git.py, chupa/journal.py, chupa/effects.py, chupa/reconcile.py, chupa/restart.py, chupa/timers.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before authoring. Read each predecessor test and direct caller the real serve-selected admission path forces. Preserve the registry floor. Before widening, grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn every caller or predecessor assertion migration under 19.L closure rules 2-5, recording every added path, reason and Context/on-demand partition in this batch's new test.

19.P3.serve-merge-admission explicitly earns chupa/runner.py and chupa/daemon.py under caller/seam-owner closure: record both additions and their existing-path partition; re-grep at this merged authoring head. Preserve the bootstrap dispatch result and inline admission signature. All production activation evidence uses the real CLI/async serve entrypoint and merged production-composition harness, injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers, never a test-only graph, live host work, real-model calls or wall-clock waits. Pin every named Tests obligation from the exact governing entry citation, including its bootstrap/inline preservation obligations, and keep record custody with its cited sole writers; do not fabricate terminals, commits or records. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer. No notify transport, recovery disposition implementation or run-lane admission is earned here.

The lookahead 19.P3.worker-recovery-disposition earns tests/test_restart_timers.py for test_restart_reuses_orphan_reconciliation's last-record-at-removal assertion under 19.L rule 2. Validate that closure at the then-merged authoring head, preserve its registry floor and pin its ordered evidence and every named recovery invariant through its own entry/row citations. This lookahead is not a payload to author here. Existing paths created by serve-activation, including chupa/serve.py and tests/test_serve.py, are now merged and use the normal Context/on-demand partition; no historical seeding snapshot is migrated.

Existing fenced paths are Context by default; On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither, including paths created by a sibling in the same admission. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded, except an explicit registry floor path retains its mandated fence and existing-path partition.

Create phase3-continue-22 as a medium/medium confirmed source: seed continuation depending on serve-merge-admission. Its suffix is admissions[22:], its next payload is worker-recovery-disposition at high/high because its row is deep, followed by phase3-continue-23 starting at admissions[23:]. Do not author those later payloads in this batch. Its fence is tickets plus only its own new tests/test_seeded_phase3_22.py. It embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's tests/test_seeded_phase3_21.py. Its Plan contract follows 19.L and section 13's exact seeder roles: 19.L, 19.I, 19.P3, section 13, 19.P3.worker-recovery-disposition, section 6, section 15 and every further next-seeder entry/citation needed from the live registry, validated through both operations before writing. Preserve its registry floor and earn caller closure by greps. Carry exact own-entry/row citations, closure greps, every named invariant obligation, record custody, Context partition and fixed authoring snapshots forward without copying entry units.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix parsed from the plan. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows, or widen a fence without an earned closure path. The suffix is a position in the live registry, never a registry duplicated in a fixture.

Create tests/test_seeded_phase3_21.py naming exactly serve-merge-admission and phase3-continue-22. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), seeder/registry edges, starts, exact implementing own-entry/row citations, registry floors and only earned additions with reasons, every named admission obligation and record custody through exact governing citations, successor exact next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record authoring head, merged idiom blob and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave both new seeds uncommitted for Check to record each requisition_review verdict in tickets/phase3-continue-21/checks.json and lift all approved seeds together through one chupa(phase3-continue-21): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; ticket paths in this code-branch commit; later payload implementation, manual HGATE release, verification filtering and unearned records.

## Scope fence
- tickets
- tests/test_seeded_phase3_21.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_21.py` exits 0 over exactly serve-merge-admission and phase3-continue-22, proving intake lint, confirmed seed birth, edges, starts and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_21.py` proves exact governing citations without copied unit bodies, earned fences, every named admission obligation and custody, successor citations/fence/merged idiom, Context closure and max-effort render feasibility from fixed snapshots.
3. At Check, `tickets/phase3-continue-21/checks.json` records requisition_review approve for both seeds, lifted together through one chupa(phase3-continue-21): seeds ticket-plane commit; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_21.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence; never invent records or widen scope. Validate only this batch's payload unit and the next-seeder lookahead unit; a later admission's unit is validated by the continuation that authors it. A required unit that is missing or lacks a SPEC DEPTH part is reported as a `premise` finding with `kind: spec_gap` and its `unit`, so section 11.4 hardens it.

## Time budget
- expected: 60m
- stuck: 90m
