---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- serve-merge-admission

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.worker-recovery-disposition
- section 6
- section 15

## Goal / Why
Advance Phase 3 by one admission, authoring the recovery payload and its successor for Check.

## Scope in / Scope out
Parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md before writing; use admissions[22:] as a live position, never a copied registry or fixture. Author only worker-recovery-disposition and phase3-continue-23. The worker payload depends on phase3-continue-22, starts high/high because its row is deep, and cites exactly 19.I, 19.P3.worker-recovery-disposition, section 6 and section 15. The successor depends on worker-recovery-disposition, starts medium/medium and begins admissions[23:]. Do not author outbox-only-admission or any later payload in this batch.

Before writing, run entry_unit_gap and resolve_plan_contract on 19.P3.worker-recovery-disposition, its row citations, section 13 and all needed next-seeder entry/citations discovered from the live registry. At this continuation's authoring head validate its next-seeder lookahead, outbox-only-admission, through those same operations. A missing or thin needed unit or omitted fact returns premise_failed with kind: spec_gap and its unit for section 11.4 hardening; never invent the contract. Only the current admission and immediate successor lookahead require validation here, not later units. Author phase3-continue-23 with the exact seeder-role Plan contract required by 19.L and section 13 for that live next admission, its row citations and needed lookahead; never resolve or cite a missing unit by guessing. This batch's parent validated only its payload and immediate recovery lookahead; it did not validate admissions[23]'s unit.

The renderer injects the implementing unit's Owner, Records, Observable and Tests bullets. Keep exact own-entry/row citations, every named invariant obligation, and record custody with their cited sole writers; never copy unit text into either seed. The full entry-unit Verification command goes into the worker seed. Its named obligations, including ordered recovery evidence, failure ordering, producing sequence, idempotence, unchanged disposition, shared startup/sweep ownership and vocabulary preservation, all remain governed by 19.P3.worker-recovery-disposition. Preserve every registry fence floor. This lookahead does not implement recovery in its parent's batch.

Pin these named Tests obligations through 19.P3.worker-recovery-disposition: test_recovery_alert_records_producing_run, test_recovery_alert_precedes_worktree_removal, test_recovery_alert_is_once_per_reaped_run, test_recovery_alert_failures_preserve_terminal_history, test_recovery_alert_does_not_change_disposition, test_every_engine_signal_name_is_listed, test_listed_signal_names_are_accepted, test_unknown_signal_name_is_refused_at_append, test_restart_reuses_orphan_reconciliation. Use its full worker Verification command: `uv run pytest tests/test_reconcile.py tests/test_restart_timers.py tests/test_cli.py tests/test_drain.py tests/test_journal.py tests/test_vocabularies.py tests/test_audit.py`. Its registry floor is chupa/reconcile.py and tests/test_reconcile.py; only mechanically earned additions extend it.

The recovery entry explicitly earns chupa/journal.py under 19.L seam-owner closure for its closed signal vocabulary registration, and tests/test_restart_timers.py under 19.L rule 2 for test_restart_reuses_orphan_reconciliation's last-record-at-removal assertion. Record both additions and the existing-path Context/on-demand partition in this batch's new test. Re-grep the then-merged head: recovery_alert, SIGNAL_NAMES, run_seq, reconcile, abandoned, journal last-record assertions, production absence assertions, public surfaces and direct callers across chupa/, eval/ and tests/. Earn every further caller or predecessor assertion migration only under 19.L rules 2-5. The exact recovery signal and ordered removal evidence belong to the cited unit, never a seeder-invented shape. Keep tests/test_vocabularies.py unchanged in the entry's preservation Verification.

Read merged reconciliation, Journal, Restart, Timers, CLI run/drain and build_daemon_core, serve composition, the production-composition harness, predecessor tests and every direct caller forced by the admission path before authoring. Preserve Journal(state_dir, clock) and append/read/close signatures, bootstrap on-entry reconciliation, ordinary DaemonTasks exception propagation and cleanup. Journal is the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer. Production evidence uses injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers through the real CLI/async serve entrypoint and merged production-composition harness when applicable; never a test-only graph, live host work, real-model calls or wall-clock waits. No notify transport or routing change is earned.

Existing fenced paths are Context by default. On-demand needs authoring-time measurements showing embedding breaches 300,000-character headroom; created paths belong in neither partition, including same-admission sibling creations. Prompt-specs and delimiter-bearing sources are never Context. Unchanged preservation suites run in Verification only, neither fenced nor embedded; an explicit registry floor retains its mandated fence and existing-path partition. Existing serve paths now use the normal merged-path partition; never migrate historical seeding snapshots.

Create tests/test_seeded_phase3_22.py naming exactly worker-recovery-disposition and phase3-continue-23, with these nine tests: test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Pin confirmed seed birth (a later rejected stamp is lifecycle history), dependencies, starts, stuck budgets, exact citations, registry floors, earned additions/reasons, every named invariant and record custody through the governing citations, successor exact next-admission/next-seeder citations and tickets/test fence. Embed tests/test_seeded_phase3_core.py as the already merged earlier idiom; never tests/test_seeded_phase3_21.py or tests/test_seeded_phase3_22.py. Record authoring head, merged idiom blob, file and ticket sizes and plan-unit lengths IN the test. Context closure and maximum-effort base render use fixed authoring snapshots, never live sizes or live plan lengths. Every stuck budget fits drain.max_ticket_minutes.

Each continuation authors just the next admission plus its successor, at most seeding.max_seeds_per_admission including the tail, depending on every payload in the preceding admission. Deep rows begin high/high; other rows begin medium/medium. The terminal phase3-exit is its sole payload with no successor; never seed past the next phase. Do not duplicate, rename, split, omit, reorder or edit registry rows. Carry closure greps, fixed authoring snapshots and cite-don't-copy forward.

Keep previously approved seeds verbatim while their bytes match ticket_sha; re-author only snagged seeds. Leave both new seeds uncommitted for Check's requisition_review. Check writes tickets/phase3-continue-22/checks.json and lifts approved seeds together through one chupa(phase3-continue-22): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages, plan/registry edits, existing tickets or run records, historical tests, ticket paths in the code commit, later implementation, manual HGATE release, verification filtering or invented records.

## Scope fence
- tickets
- tests/test_seeded_phase3_22.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_22.py` exits 0 over exactly the next payload and successor, proving grammar, confirmed birth, dependencies, starts and bounded stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_22.py` pins citations without duplicated unit prose, all named recovery obligations/custody, earned closure, successor roles and fixed-snapshot render feasibility.
3. `tickets/phase3-continue-22/checks.json` records requisition_review approve for both seeds before their single ticket-plane lift; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with all existing tests retained and production behavior unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_22.py
uv run pytest -q
```

## Definition of rejected
A governing entry lacks a required fact or contradicts merged behavior, or a criteria-forced edit cannot be earned under the fence: return premise_failed naming the unit for section 11.4 hardening. Never invent missing facts.

## Time budget
- expected: 60m
- stuck: 90m
