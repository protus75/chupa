---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- kill-signal-journal
- kill-executor-abort

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- section 20
- 19.P3.kill-worker-stop
- 19.P3.kill-failure-suppression
- 19.P3.kill-cli-activation
- section 6
- section 11

## Goal / Why
Advance Phase 3 by exactly one admission: author kill-worker-stop, kill-failure-suppression and phase3-continue-12 as confirmed seeds, uncommitted for Check to review and lift together. This is continuation 11; its shrinking suffix is admissions[11:] in the live registry, and its successor starts at admissions[12:].

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md. Read admissions[11:] and each complete entry unit, never a copied registry. Run entry_unit_gap and resolve_plan_contract for 19.P3.kill-worker-stop, 19.P3.kill-failure-suppression and 19.P3.kill-cli-activation, resolve section 13, section 20, section 6, section 11 and every further needed citation. Validate every entry/citation needed by phase3-continue-12 through both operations before carrying its contract. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only kill-worker-stop, kill-failure-suppression and phase3-continue-12. Both implementing seeds start medium/medium and depend on phase3-continue-11; kill-failure-suppression also explicitly depends on kill-worker-stop. Their exact Plan contracts are respectively 19.I, 19.P3.kill-worker-stop, section 20 and 19.I, 19.P3.kill-failure-suppression, section 20. Each seed cites its own complete entry unit through Plan contract; the renderer injects its governing Owner, Records, Observable and Tests bullets verbatim. Never copy unit text into a seed or into this seeding ticket. Add only seed-specific edges, starts, fence floors, earned closure paths and the full entry-unit Verification command. Pin exact citations rather than duplicated unit bodies in the seeding test. Carry this cite-don't-copy rule forward to phase3-continue-12.

The cited 19.P3.kill-worker-stop and 19.P3.kill-failure-suppression units govern every owner, exact record shape, sole writer, observable, named invariant test and full Verification command. Preserve each live registry fence floor. Read merged kill-signal-journal and kill-executor-abort and the real ControlInbox, ControlProjection, Driver.abort_current and DaemonTasks operations and direct callers before authoring. No replacement control implementation, abort path, task owner or failure routing is earned. Explicit tests use the real predecessor boundaries, injected seams, disposable directories and asyncio barriers, never real-model calls or wall-clock waits.

Before widening, grep flipped symbols, old assertion values, public surfaces and direct callers across chupa/, eval/ and tests/. In particular grep abort_current, timeout ownership, optional review waits, cancellation handling, DaemonTasks task ownership, ordinary failure callbacks, public-operation allowlists and production absence assertions. Driver construction and run signatures remain unchanged. Add only earned 19.L closure rules 2-5 paths, recording every path, reason and Context/on-demand partition in this batch's new test. Existing fenced paths are Context by default; On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded. Never migrate historical seeding tests.

Use calibrated raising probes over real CLI run/drain and the merged production-composition harness: deliberate wiring must trip the probe and ordinary composition must leave it untouched. chupa.daemon is already reachable; import absence is not dormancy evidence. Preserve shared admission and dispatch hold semantics, bootstrap inline admission, ordinary DaemonTasks exception propagation and cleanup. Construction remains dormant; executor unwind precedes worker cancellation and matching durable acceptance authorizes stopping/suppression as the cited units require. Out: Phase 3 implementation in this batch, concurrent polling, CLI kill activation, background startup, serve wiring, altered signatures, new durable flags or applied records.

Create phase3-continue-12 as a medium/medium confirmed source: seed continuation depending on both kill-worker-stop and kill-failure-suppression. Its suffix is admissions[12:], its next payload is kill-cli-activation, followed by phase3-continue-13 starting at admissions[13:]. Do not author those later payloads in this batch. Its fence is tickets plus only its own new tests/test_seeded_phase3_12.py. It embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's tests/test_seeded_phase3_11.py. Its Plan contract follows 19.L and section 13's exact seeder roles: 19.L, 19.I, 19.P3, section 13, section 20, 19.P3.kill-cli-activation and every further next-seeder entry/citation needed from the live registry, validated before writing. kill-cli-activation depends on phase3-continue-12, starts high/high as a deep row, and cites exactly 19.I, 19.P3.kill-cli-activation, section 20. Preserve its registry floor and earn any activation/caller closure through greps. The worker-stop and failure-suppression suites remain unchanged preservation suites at kill-cli-activation; serve-activation owns their production wiring and dormancy migrations. Carry exact own-entry/row citations, closure greps, named invariant obligations, record custody, Context partition and fixed authoring snapshots forward without copying entry units.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix parsed from the plan. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows, or widen a fence without an earned closure path. The suffix is a position in the live registry, not a registry duplicated in a fixture.

Create tests/test_seeded_phase3_11.py naming exactly kill-worker-stop, kill-failure-suppression and phase3-continue-12. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), seeder/registry edges, medium/medium starts, exact implementing own-entry/row citations, registry floors and only earned additions with reasons, complete dormant kill obligations and record custody through exact governing citations, successor exact next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record authoring head, merged idiom blob and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Never migrate historical seeding tests.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave all three new seeds uncommitted for Check to record each requisition_review verdict in tickets/phase3-continue-11/checks.json and lift all approved seeds together through one chupa(phase3-continue-11): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; ticket paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_11.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_11.py` exits 0 over exactly kill-worker-stop, kill-failure-suppression and phase3-continue-12, proving intake lint, confirmed seed birth, edges, starts and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_11.py` proves exact governing own-entry/row citations without copied unit bodies, earned fences, dormant kill obligations/custody, successor citations/fence/merged idiom, Context closure and max-effort render feasibility from fixed snapshots.
3. At Check, `tickets/phase3-continue-11/checks.json` records requisition_review approve for all three seeds, lifted together through one chupa(phase3-continue-11): seeds ticket-plane commit; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_11.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or incomplete contract for section 11.4 hardening if a needed fact is omitted or the criteria force an unearned path outside the fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
