---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- dispatch-admission-boundary
- dispatch-config-snapshot

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.scheduler-activation
- 19.P3.merge-queue-activation
- 19.P3.rework-activation

## Goal / Why
Advance Phase 3 by exactly one admission: author scheduler-activation and phase3-continue-06 as confirmed seeds, left uncommitted for this ticket's Check to review and lift together. This is continuation 05. Parse the YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md; the shrinking unseeded suffix is admissions[5:]. Its next payload is scheduler-activation alone and its successor starts at admissions[6:]. Never copy the registry into a repository file or alter its rows.

## Scope in / Scope out
Before writing, parse the current registry, read its next row and complete entry unit, and run entry_unit_gap and resolve_plan_contract for every entry unit either authored payload or successor needs: 19.P3.scheduler-activation, 19.P3.merge-queue-activation and 19.P3.rework-activation. Read any further unit a needed citation requires. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening; never invent facts.

Create scheduler-activation only from its registry row and complete own-entry unit, high/high because deep: true, depending on phase3-continue-05. It cites exactly 19.I and 19.P3.scheduler-activation. Preserve its registry fence floor. Add only paths earned by 19.L closure rules 2-5, after grepping symbols and old assertion values across chupa/, eval/ and tests/, and record each addition and reason in this batch's test. Fence every predecessor dormancy/negative assertion and composition caller the flip forces. In particular, add tests/test_daemon_config.py under ACTIVATION/CONTRADICTED TESTS and embed it by default because test_config_snapshot_is_dormant pins daemon import absence; preserve the predecessor's component behavior and bootstrap CLI checks. Existing fenced paths are Context by default; On-demand requires recorded authoring-time measurements proving embedding breaches headroom. Created paths belong in neither. Prompt-specs and delimiter-bearing sources are never Context. Keep preservation suites unchanged, Verification-only, neither fenced nor embedded.

Name every entry-unit owner, exact record shape and writer, observable and named test obligation in the payload. chupa/daemon.py owns the production core factory; chupa/__main__.py owns its real root binding; tests/test_daemon_composition.py calls that root rather than a parallel graph. Compose one shared journal, Scheduler, Watcher, DaemonAdmission and snapshot_dispatch; wire publish/update, remove/remove and dispatch/admission. Root inputs retain ticket text-or-None reads, stem change delivery, the committed plan, Clock, Sleep and seconds debounce. The existing config loader and explicit --config or checkout-relative path remain authoritative. Bind every dispatch-local pipeline consumer to the same immutable snapshot, captured once inside the serial slot. Scheduler and watcher retain their policy and record custody, including WATCHER_PARSE_FAILURE's exact signal body, and runner/drain/intake/merge retain accounting and terminals. Add no durable record or config key.

The real production graph becomes reachable in the transitive CLI import closure recognizing both import idioms. Construction of the graph starts no host work, snapshot load or background task. Injected-seam tests drive watcher edits/removal, last-known-good parse behavior, eligibility/age/backpressure, no P0 preemption, single-flight cleanup and cancellation, stable active snapshots, next valid edits and invalid reload without fallback. Preserve bootstrap run/drain dispatch, reconciliation, retry accounting, lock lifetime and inline merge. Migrate the negative closure assertions in test_scheduler_and_watcher_are_dormant, test_daemon_admission_is_dormant and test_config_snapshot_is_dormant to positive production reachability/graph evidence, retaining every other component assertion. Use all eight named tests in 19.P3.scheduler-activation and run its complete Verification command including unchanged tests/test_config.py, tests/test_cli.py and tests/test_drain.py. Later machinery stays with its own rows.

Create phase3-continue-06 as a medium/medium confirmed source: seed continuation depending on scheduler-activation. Its suffix is admissions[6:], its next payload is merge-queue-activation and rework-activation, followed by phase3-continue-07 starting at admissions[7:]. The Rework seed explicitly depends on its merge-queue-activation sibling as well as its seeder. It fences tickets plus only its own new tests/test_seeded_phase3_06.py and embeds an already merged earlier seeding test as idiom (tests/test_seeded_phase3_core.py), never this batch's new test. It cites 19.L, 19.I, 19.P3, section 13, 19.P3.merge-queue-activation and 19.P3.rework-activation, plus any complete entry units its own successor needs under 19.L. Before writing, that continuation parses its suffix, reads and gap-checks/resolves both activation entry units and every further required citation; missing/incomplete needed units return premise_failed naming their ids for section 11.4 hardening, never invented facts. Do not author any payload beyond scheduler-activation in this batch.

The merge/rework activation entry units govern continuation 06: compose the queue in the existing production pipeline binding and extend this same real harness; preserve bootstrap inline admission. Caller closure adds chupa/runner.py for merge-queue activation. Rework consumes the original ConflictHandoff only after queue unwind and applies exact reviewed proposals through the lock-owning ticket-plane writer, preserving record writers, publication-before-supersedes-before-retirement, fresh approvals, terminal order, lineage caps and transitive successor dependency folds. Its explicit closure additions include chupa/runner.py, chupa/drain.py, chupa/scheduler.py, tests/test_ladder.py, tests/test_drain.py, tests/test_scheduler.py, tests/test_reject_queue.py and tests/test_diagnose.py. Re-grep at that merged authoring head for every further mechanically forced caller/negative assertion. Carry every entry-unit named invariant test and exact record shape into those future payloads; never invent a replacement graph or record.

Each continuation authors only its next admission and successor under 19.L, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Row fences remain floors with only earned closure additions. Each continuation depends on every payload of the previous admission and carries the next shrinking suffix. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase.

Create tests/test_seeded_phase3_05.py naming exactly scheduler-activation and phase3-continue-06. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), both dependency edges, high/high and medium/medium starts, exact implementing own-entry/row citations, registry fence floors and only earned closure additions with reasons, successor next-admission/next-seeder cites, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure, authoring-time sizes and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots and test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Record the merged idiom and measurements. Never migrate historical seeding tests.

An approve holds on retry while bytes match its ticket_sha; keep previously approved seeds verbatim and re-author only snagged seeds. Check records each requisition_review verdict and lifts both approved seeds together through the ticket-plane lane. Commit only this ticket's new test, leaving new seed ticket files uncommitted.

Out: Phase 3 implementation; any payload beyond scheduler-activation and phase3-continue-06; Suggestion Box messages; plan/registry changes; existing tickets, run records and historical tests; tickets paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_05.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_05.py` exits 0 over exactly scheduler-activation and phase3-continue-06, proving intake lint, confirmed seed birth, stuck budgets within the drain envelope, both dependency edges and correct high/high versus medium/medium starts.
2. `uv run pytest -q tests/test_seeded_phase3_05.py` proves exact own-entry/row citations, fence floors with only recorded earned closure additions including tests/test_daemon_config.py, complete activation transition closure, successor next-admission/next-seeder cites, tickets/test fence, merged earlier idiom, Context closure and maximum-effort base render feasibility from fixed authoring snapshots.
3. At Check, `tickets/phase3-continue-05/checks.json` records requisition_review approve for both seeds, which reach main together through one chupa(phase3-continue-05): seeds ticket-plane commit. Leave new seed files uncommitted; this branch commits only its new test and no tickets path.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_05.py
uv run pytest -q
```

## Definition of rejected
Reject if a registry row is copied, altered, reordered, renamed, split, omitted or widened without an earned closure path; an implementing payload cites the whole phase or a sibling entry; a seed invents a fact or lacks a named invariant test; activation omits a predecessor negative fixture or forced composition caller; a seed is filed through the box, committed on the code branch or authored past this admission; or an edit leaves the fence. Missing/incomplete entry units return premise_failed naming ids for section 11.4 hardening before regeneration. Within-admission consumption declares a sibling edge under section 13.3.

## Time budget
- expected: 60m
- stuck: 90m
