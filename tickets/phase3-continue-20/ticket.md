---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- checkpoint-push

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.serve-activation
- section 18
- section 20
- 19.P3.serve-merge-admission
- section 9

## Goal / Why
Advance Phase 3 by exactly one admission: author serve-activation and phase3-continue-21 as confirmed seeds, uncommitted for Check to review and lift together.

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md. Read admissions[20:] and each complete needed entry unit, never a copied registry. Run entry_unit_gap and resolve_plan_contract for 19.P3.serve-activation and every further next-seeder entry/citation needed from the live registry, resolving row citations and section 13, section 18, section 20 and section 9. The next-seeder lookahead is 19.P3.serve-merge-admission with section 9. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only serve-activation and phase3-continue-21. serve-activation depends on phase3-continue-20, starts high/high because its registry row is deep, and cites exactly 19.I, 19.P3.serve-activation, section 18 and section 20. Its complete entry unit governs every owner, record shape, sole writer, observable, named invariant test and full Verification command. The renderer injects Owner, Records, Observable and Tests bullets verbatim. Never copy unit text into a seed or into this seeding ticket. Add only seed-specific edges, starts, registry fence floors, earned closure paths and the full entry-unit Verification command. Pin exact own-entry/row citations, every named invariant obligation and record custody through governing citations rather than duplicated unit bodies. Carry this cite-don't-copy rule forward to phase3-continue-21.

Read merged chupa/daemon.py, chupa/__main__.py, chupa/runner.py, chupa/stages.py, chupa/merge.py, chupa/mergequeue.py, chupa/control.py, chupa/scheduler.py, chupa/watcher.py, chupa/triage.py, chupa/heartbeat.py, chupa/restart.py, chupa/timers.py, chupa/checkpoint.py, chupa/git.py, chupa/journal.py, chupa/effects.py, chupa/box.py, chupa/storm.py, chupa/config.py, real CLI run/drain and build_daemon_core, and the merged production-composition harness before authoring. Read each predecessor test and direct caller the real serve graph forces. Preserve the registry floor. Before widening, grep flipped symbols, old assertion values, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn every caller or predecessor assertion migration under 19.L closure rules 2-5, recording every added path, reason and Context/on-demand partition in this batch's new test.

Authoring admission 19 found tests/test_restart_timers.py::test_restart_construction_is_idle pins the CLI serve verb's absence. Re-grep at this authoring head and earn tests/test_restart_timers.py under rules 2-3 to migrate only that assertion while preserving startup/timer invariants. Also earn the now-merged tests/test_checkpoint.py for its test_checkpoint_boundary_is_dormant activation assertion, as the governing serve entry requires. These are closure facts to validate, not a replacement for the live registry or full caller greps. chupa/checkpoint.py and tests/test_checkpoint.py were created by the prior admission: after checkpoint-push merges they are existing paths and follow the normal Context/on-demand partition. No historical seeding snapshot is migrated.

Keep existing composition callers valid without a second production path. All production activation evidence uses the real CLI/async serve entrypoint and merged production-composition harness, injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers, never a test-only graph, live host work, real-model calls or wall-clock waits. Preserve Journal(state_dir, clock) and append/read/close signatures and all direct callers, bootstrap on-entry reconciliation, inline admission and ordinary DaemonTasks exception propagation and cleanup. Journal remains the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer. No caller-read records, replacement writers, notify transport or daemon-admission routing are earned here; serve-merge-admission owns the later routing activation.

Existing fenced paths are Context by default; On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither, including paths created by a sibling in the same admission. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded, except an explicit registry floor path retains its mandated fence and existing-path partition.

Create phase3-continue-21 as a medium/medium confirmed source: seed continuation depending on serve-activation. Its suffix is admissions[21:], its next payload is serve-merge-admission at high/high because its row is deep, followed by phase3-continue-22 starting at admissions[22:]. Do not author those later payloads in this batch. Its fence is tickets plus only its own new tests/test_seeded_phase3_21.py. It embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's tests/test_seeded_phase3_20.py. Its Plan contract follows 19.L and section 13's exact seeder roles: 19.L, 19.I, 19.P3, section 13, 19.P3.serve-merge-admission, section 9 and every further next-seeder entry/citation needed from the live registry, validated through both operations before writing. Preserve its registry floor and earn caller closure by greps. Carry exact own-entry/row citations, closure greps, every named invariant obligation, record custody, Context partition and fixed authoring snapshots forward without copying entry units. 19.P3.serve-merge-admission and section 9 are required next-seeder lookahead, not payloads to author here.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix parsed from the plan. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows, or widen a fence without an earned closure path. The suffix is a position in the live registry, never a registry duplicated in a fixture.

Create tests/test_seeded_phase3_20.py naming exactly serve-activation and phase3-continue-21. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), seeder/registry edges, starts, exact implementing own-entry/row citations, registry floors and only earned additions with reasons, every named serve obligation and record custody through exact governing citations, successor exact next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record authoring head, merged idiom blob and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave both new seeds uncommitted for Check to record each requisition_review verdict in tickets/phase3-continue-20/checks.json and lift all approved seeds together through one chupa(phase3-continue-20): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; ticket paths in this code-branch commit; later payload implementation, manual HGATE release, verification filtering and unearned records.

## Scope fence
- tickets
- tests/test_seeded_phase3_20.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_20.py` exits 0 over exactly serve-activation and phase3-continue-21, proving intake lint, confirmed seed birth, edges, starts and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_20.py` proves exact governing citations without copied unit bodies, earned fences, every named serve obligation and custody, successor citations/fence/merged idiom, Context closure and max-effort render feasibility from fixed snapshots.
3. At Check, `tickets/phase3-continue-20/checks.json` records requisition_review approve for both seeds, lifted together through one chupa(phase3-continue-20): seeds ticket-plane commit; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_20.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming a missing or contradictory entry-unit fact for section 11.4 hardening, or a criteria-forced path that cannot be earned inside this fence; never invent records or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
