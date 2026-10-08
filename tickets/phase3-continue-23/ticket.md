---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- worker-recovery-disposition

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.outbox-only-admission
- section 10
- 19.P3.daemon-soak

## Goal / Why
Advance Phase 3 by one admission, authoring outbox-only-admission and phase3-continue-24 for Check to review and lift.

## Scope in / Scope out
Before writing, parse YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md; admissions[23:] is the live position, never a copied registry or fixture. Author only outbox-only-admission and phase3-continue-24. The payload depends on phase3-continue-23 and starts high/high because its row is deep. Its Plan contract is exactly 19.I, 19.P3.outbox-only-admission, 19.L and section 10. The successor depends on outbox-only-admission, starts medium/medium and begins admissions[24:]. Do not author daemon-soak or later payloads in this batch.

Run entry_unit_gap and resolve_plan_contract on the current admission, its row citations, section 13 and each needed next-seeder entry/citation discovered from the live registry before authoring. Validate the immediate lookahead, 19.P3.daemon-soak, at this authoring head; only the current admission and immediate successor lookahead require validation, never later units. This parent validated outbox-only-admission, not the successor's lookahead. A missing or thin needed unit or omitted fact returns premise_failed with kind: spec_gap and that unit for section 11.4 hardening. Never guess an Owner, record shape, observable or named test. All Phase 3 registry rows are hardenable under section 11.4.

The renderer supplies the implementing unit's Owner, Records, Observable and Tests bullets. Preserve exact own-entry/row citations, every named invariant obligation and record custody with the cited sole writers; never copy unit text into either seed. Put the full entry-unit Verification command in the payload: `uv run pytest tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_cli.py tests/test_drain.py tests/test_audit.py tests/test_checkpoint.py`. Pin these named obligations through 19.P3.outbox-only-admission: test_outbox_only_check_accepts_registered_report, test_outbox_only_check_requires_current_report, test_outbox_only_check_failure_never_admits, test_outbox_only_admission_records_null_commit_and_retires, test_outbox_only_merge_regate_requires_lift_custody and test_outbox_only_exception_preserves_code_lane_safety. Preserve its named empty-ok, already-satisfied, report-purge, schema-validation and checks-custody predecessor obligations. Current-run output, purge before Verification, matching lift custody, null-commit settlement, unchanged code tree, retirement, replay, approval and code-lane safety remain governed by that unit.

Read merged stages, merge, MergeQueue, runner, daemon, CLI run/drain and build_daemon_core, serve composition, Journal, Restart, Timers, the production-composition harness and every predecessor test/direct caller forced by the admission path. The payload's registry floor is chupa/stages.py, chupa/merge.py, tests/test_stages.py and tests/test_merge.py. Re-grep flipped empty-diff assertions, Admission.commit, write_squash, gather_evidence, report purge/lift, public surfaces, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn every addition only under 19.L rules 2-5 or cited seam-owner closure; record the exact path, reason and existing-path Context/on-demand partition in this batch's test. Preserve every registry fence floor. No signature change or further fence widening is presumed from this lookahead.

Journal is the sole durable event writer, Box the sole queue-record writer and ControlInbox the sole control-decision writer. Keep Journal(state_dir, clock) and append/read/close signatures, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The existing checks lift alone commits registered reports; the shared admission writer owns merge evidence. Production evidence uses injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers through the real CLI/async serve entrypoint and merged production-composition harness when applicable. Never use a test-only graph, live host work, real-model calls or wall-clock waits. No notify transport or routing change is earned.

Existing fenced paths are Context by default. On-demand requires authoring-time measurements proving embedding breaches 300,000-character headroom. Created paths belong in neither partition, including same-admission sibling creations. Prompt-specs and delimiter-bearing sources are never Context. Unchanged preservation suites run in Verification only, neither fenced nor embedded, except an explicit registry floor retains its required fence and existing-path partition. Serve paths now follow the normal merged-path partition; never migrate historical seeding snapshots.

Create phase3-continue-24 with the exact seeder-role Plan contract required by 19.L and section 13 for its live next admission, row citations and needed lookahead. Its fence is tickets and its own new tests/test_seeded_phase3_24.py, and its Context embeds tests/test_seeded_phase3_core.py as the merged earlier idiom, never this admission's test. Carry cite-don't-copy, closure greps, named invariant obligations and sole-writer custody forward. It authors daemon-soak plus phase3-continue-25, whose position is admissions[25:], only after validating its own needed units; this batch implements neither soak machinery nor run-lane admission.

Create tests/test_seeded_phase3_23.py naming exactly outbox-only-admission and phase3-continue-24, with test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots and test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Pin confirmed seed birth (a later rejected stamp is lifecycle history), dependencies, starts, bounded stuck budgets, exact citations, floors, earned additions/reasons, all named invariant obligations and record custody through governing citations, successor exact next-admission/next-seeder citations and tickets/test fence. Record authoring head, merged idiom blob, file and ticket sizes and plan-unit lengths IN the test. Context closure and maximum-effort base render use fixed authoring snapshots, never live sizes or live plan lengths. Embed tests/test_seeded_phase3_core.py, never tests/test_seeded_phase3_22.py or tests/test_seeded_phase3_23.py. Every stuck budget fits drain.max_ticket_minutes.

Each continuation authors only the next admission and its successor, at most seeding.max_seeds_per_admission including the tail, depending on every payload of the preceding admission. Deep rows start high/high; other rows medium/medium. Terminal phase3-exit is its sole payload with no successor; never seed past the next phase. Do not duplicate, rename, split, omit, reorder or edit registry rows.

Keep previously approved seeds verbatim while bytes match ticket_sha; re-author only snagged seeds. Leave both new seeds uncommitted for Check's requisition_review. Check records approve for both in tickets/phase3-continue-23/checks.json and lifts them together through one chupa(phase3-continue-23): seeds ticket-plane commit. Commit only this ticket's new test. Out: Suggestion Box messages, plan/registry edits, existing tickets/run records, historical tests, ticket paths in the code commit, later implementation, manual HGATE release, verification filtering and invented records.

## Scope fence
- tickets
- tests/test_seeded_phase3_23.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_23.py` exits 0 over exactly the payload and successor, proving intake lint, confirmed birth, dependencies, starts and bounded stuck budgets.
2. `uv run pytest -q tests/test_seeded_phase3_23.py` pins exact citations without copied prose, every named invariant and custody, earned closure, successor roles and fixed-snapshot render feasibility.
3. At Check, `tickets/phase3-continue-23/checks.json` records requisition_review approve for both seeds before their single ticket-plane lift; leave seed files uncommitted and commit only the new test.
4. `uv run pytest -q` exits 0 with existing tests retained and production behavior unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_23.py
uv run pytest -q
```

## Definition of rejected
Return premise_failed for a missing, thin or contradictory needed governing unit, naming kind: spec_gap and that unit for section 11.4 hardening; never invent facts. A criteria-forced edit that cannot be earned inside the fence also returns premise_failed. Validate only the current payload and immediate successor lookahead, not later units.

## Time budget
- expected: 60m
- stuck: 90m
