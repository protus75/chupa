---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- kill-worker-stop
- kill-failure-suppression

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- section 20
- 19.P3.kill-cli-activation
- 19.P3.heartbeat
- 19.P3.restart-timers
- section 9
- section 15
- section 6
- section 11

## Goal / Why
Advance Phase 3 by exactly one admission: author kill-cli-activation and phase3-continue-13 as confirmed seeds, uncommitted for Check to review and lift together. Continuation 12 reads admissions[12:] in the live registry; its successor starts at admissions[13:].

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md. Read admissions[12:] and each complete needed entry unit, never a copied registry. Run entry_unit_gap and resolve_plan_contract for 19.P3.kill-cli-activation, 19.P3.heartbeat and 19.P3.restart-timers and resolve every needed row citation and section 13, section 20, section 9, section 15, section 6 and section 11. Validate every further entry/citation needed by phase3-continue-13 before carrying its contract. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only kill-cli-activation and phase3-continue-13. kill-cli-activation depends on phase3-continue-12, starts high/high as a deep row, and cites exactly 19.I, 19.P3.kill-cli-activation, section 20. Its complete entry unit governs every owner, record shape, sole writer, observable, named invariant test and full Verification command. The renderer injects its Owner, Records, Observable and Tests bullets verbatim. Never copy unit text into a seed or into this seeding ticket. Add only seed-specific edges, starts, registry fence floors, earned closure paths and the full entry-unit Verification command. Pin exact citations rather than duplicated unit bodies in the seeding test. Carry this cite-don't-copy rule forward to phase3-continue-13.

Read merged kill-signal-journal, kill-executor-abort, kill-worker-stop and kill-failure-suppression and the real ControlInbox, ControlProjection, PauseConsumer, Driver.abort_current, StageContext, TicketWriter, runner.bind, Pipeline/Dispatch, drain and CLI operations and direct callers before authoring. Preserve the predecessor control implementation, executor abort path and shared admission/dispatch hold semantics. The cited activation unit owns the live bootstrap drain behavior and record custody; do not invent a second executor, control inbox, timer, failure route or task graph.

Before widening, grep flipped symbols, old assertion values, public surfaces and direct callers across chupa/, eval/ and tests/. In particular grep abort_current, timeout ownership, optional review waits, cancellation handling, DaemonTasks task ownership, ordinary failure callbacks, public-operation allowlists, CLI verbs, production absence assertions, StageContext/TicketWriter forwarding and drain composition. Preserve Driver construction/run and existing composition/callable signatures. Earn any activation/caller closure through greps under 19.L closure rules 2-5, recording every added path, reason and Context/on-demand partition in this batch's new test. Migrate only criteria-forced predecessor assertions, never historical seeding tests. The registry floor already fences tests/test_kill_signal_journal.py and tests/test_kill_executor_abort.py for their activation assertions. Any further criteria-forced caller or dormancy migration must be earned and fenced, never silently worked around.

Existing fenced paths are Context by default; On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded. In particular the worker-stop and failure-suppression suites remain unchanged preservation suites at kill-cli-activation; serve-activation owns their production wiring and dormancy migrations. Use calibrated raising probes over real CLI run/drain and the merged production-composition harness: deliberate wiring must trip the probe and ordinary composition must leave it untouched. chupa.daemon is already reachable; import absence is not dormancy evidence. Explicit tests use real predecessor boundaries, injected seams, scripted LLMs, disposable repositories and asyncio barriers, never real-model calls or wall-clock waits. Preserve bootstrap inline admission, ordinary DaemonTasks exception propagation and cleanup. Out: Phase 3 implementation in this batch, worker boundary activation, background startup, serve wiring, replacement control/abort paths, altered signatures and unearned records.

Create phase3-continue-13 as a medium/medium confirmed source: seed continuation depending on kill-cli-activation. Its suffix is admissions[13:], its next payload is heartbeat, followed by phase3-continue-14 starting at admissions[14:]. Do not author those later payloads in this batch. Its fence is tickets plus only its own new tests/test_seeded_phase3_13.py. It embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's tests/test_seeded_phase3_12.py. Its Plan contract follows 19.L and section 13's exact seeder roles: 19.L, 19.I, 19.P3, section 13, 19.P3.heartbeat, section 9, section 15 and every further next-seeder entry/citation needed from the live registry, validated through both operations before writing. heartbeat depends on phase3-continue-13, starts medium/medium, and cites exactly 19.I, 19.P3.heartbeat, section 9, section 15. Preserve its registry floor and earn caller closure by greps; serve-activation owns heartbeat production wiring. The next deep row restart-timers starts high/high and cites exactly 19.I, 19.P3.restart-timers, section 6, section 15 when its admission is reached. Carry exact own-entry/row citations, closure greps, named invariant obligations, record custody, Context partition and fixed authoring snapshots forward without copying entry units.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix parsed from the plan. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows, or widen a fence without an earned closure path. The suffix is a position in the live registry, not a registry duplicated in a fixture.

Create tests/test_seeded_phase3_12.py naming exactly kill-cli-activation and phase3-continue-13. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), seeder/registry edges, starts, exact implementing own-entry/row citations, registry floors and only earned additions with reasons, complete activation obligations and record custody through exact governing citations, successor exact next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record authoring head, merged idiom blob and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Never migrate historical seeding tests.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave both new seeds uncommitted for Check to record each requisition_review verdict in tickets/phase3-continue-12/checks.json and lift all approved seeds together through one chupa(phase3-continue-12): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; ticket paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_12.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_12.py` exits 0 over exactly kill-cli-activation and phase3-continue-13, proving intake lint, confirmed seed birth, edges, starts and stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_12.py` proves exact governing own-entry/row citations without copied unit bodies, earned activation/caller fences, complete kill obligations/custody, successor citations/fence/merged idiom, Context closure and max-effort render feasibility from fixed snapshots.
3. At Check, `tickets/phase3-continue-12/checks.json` records requisition_review approve for both seeds, lifted together through one chupa(phase3-continue-12): seeds ticket-plane commit; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_12.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed naming the missing or incomplete contract for section 11.4 hardening if a needed fact is omitted or the criteria force an unearned path outside the fence. Never invent records, replacement graphs or later production behavior.

## Time budget
- expected: 60m
- stuck: 90m
