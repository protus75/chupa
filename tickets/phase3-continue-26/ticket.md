---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- daemon-soak-runner

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.soak-run

## Goal / Why
Author the separate soak report producer and the terminal-admission continuation for Check to review and lift.

## Scope in / Scope out
Parse the YAML between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 directly from CHUPA_PLAN.md before writing. Begin admissions[26:]: soak-run, then phase3-exit. Author only soak-run and phase3-continue-27. The producer starts medium/medium and depends on phase3-continue-26, transitively after daemon-soak, daemon-soak-runner and outbox-only-admission. Cite exactly 19.I and 19.P3.soak-run plus the live row citations (currently none). The successor starts medium/medium, depends on soak-run and begins admissions[27:]. Its seeder-role citations include 19.L, 19.I, 19.P3 and section 13; terminal lookahead is governed by 19.P3. Do not author phase3-exit here.

Run entry_unit_gap and resolve_plan_contract for the current admission, live row citations, section 13 and needed next-seeder citations at the authoring head. Validate only the current admission and immediate terminal lookahead, never later units. The terminal phase3-exit is governed by 19.P3 rather than a non-exit entry. The parent checked soak-run, not the terminal. Missing/thin units or omitted needed facts return premise_failed with kind: spec_gap naming the owning cited unit for section 11.4 hardening. All Phase 3 rows are hardenable. Never invent an Owner, record shape, observable or named test. The renderer injects Owner, Records, Observable and Tests: cite, never copy unit text. Carry exact own-entry/row citations, named invariant obligations and record custody forward.

The producer's entry governs fresh current-run output, its sole deliverable, provenance, command and existing lane custody. Its registry floor is the named report path only; it owns no code or test module. Leave that report uncommitted for the checks lift. Read the merged runner, canonical writer, artifacts schema, stages report purge/lift/validation and merge run-lane admission, Git/Effects and every forced predecessor/direct caller. Re-grep public produce/write_report surfaces, KNOWN_ARTIFACTS, Artifact, public surfaces/allowlists, absence assertions and direct callers across chupa/, eval/ and tests/. Earn additions only through 19.L rules 2-5 or cited seam-owner closure; no public signature change or extra fence is presumed from lookahead. Record exact paths and reasons plus the existing-path Context/on-demand partition in the batch test.

Pin test_daemon_soak_command_writes_report_only_on_green, test_daemon_soak_requires_member_local_evidence and test_daemon_soak_is_rederivable via 19.P3.soak-run. Carry the merged schema/writer/lift predecessors test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift and report-purge/schema-validation/named-report-required/checks-only/inherited byte-equal exclusion obligations test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report. Carry test_outbox_only_check_accepts_registered_report and test_outbox_only_admission_records_null_commit_and_retires. The producer Verification runs uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py and uv run pytest tests/test_stages.py tests/test_merge.py unchanged, followed by uv run python -m eval.daemon_soak --out tickets/soak-run/daemon-soak-report.json. These unchanged preservation suites are neither fenced nor embedded. No test-authored report substitutes for production evidence.

Journal alone writes durable events; Box alone writes queue records; ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The checks lift alone commits registered reports.

Existing fenced paths are Context by default. On-demand requires measured embedding beyond 300,000-character headroom. Created paths belong in neither partition, including same-admission sibling creations. Exclude prompt-specs and delimiter-bearing sources from Context. Serve retains its normal merged-path partition; never migrate historical seeding snapshots. Only tests/test_seeded_phase3_core.py is the merged earlier idiom; never embed tests/test_seeded_phase3_25.py or tests/test_seeded_phase3_26.py.

Create the new batch test naming exactly soak-run and phase3-continue-27. Use the named assertions test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Pin confirmed seed birth (later rejection is lifecycle history), exact dependencies, starts and budgets bounded by drain.max_ticket_minutes, citation roles, earned closure/reasons, named obligations/custody and successor suffix. Record authoring head, merged idiom blob, file and ticket sizes and plan-unit lengths IN that test. Context closure and maximum-effort base render use fixed authoring snapshots, never live sizes or live plan lengths.

The chain emits only its next admission and successor within seeding.max_seeds_per_admission including the tail, depending on every preceding payload. Deep rows start high/high; ordinary rows medium/medium. Terminal phase3-exit is high/high and is its seeder's sole payload without a successor. Never seed past the next phase, or duplicate, rename, split, omit, reorder or edit registry rows. Keep previously approved seeds verbatim while bytes match ticket_sha; re-author only snagged seeds. Leave both new seeds uncommitted for Check's requisition_review. Check records approve for both in tickets/phase3-continue-26/checks.json and lifts them together through one chupa(phase3-continue-26): seeds ticket-plane commit. Commit only the new test. Out: Box messages, plan edits, existing tickets/run records, historical tests, ticket paths in the code commit, later implementation, manual HGATE release, verification filtering and invented records.

## Scope fence
- tickets
- tests/test_seeded_phase3_26.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_26.py` exits 0 proving the two exact stems, confirmed birth, lint, dependencies, starts and drain-bounded budgets.
2. `uv run pytest -q tests/test_seeded_phase3_26.py` exits 0 pinning citations, named obligations/custody, earned closure and fixed-snapshot render feasibility.
3. `tickets/phase3-continue-26/checks.json` records requisition_review approve for both before one ticket-plane seed lift; seeds remain uncommitted and only the new test is committed.
4. `uv run pytest -q` exits 0 with production behavior unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_26.py
uv run pytest -q
```

## Definition of rejected
A missing needed contract fact returns premise_failed, kind: spec_gap, naming its governing cited unit for section 11.4 hardening. A forced path beyond the earned fence returns premise_failed; never invent or widen the contract.

## Time budget
- expected: 60m
- stuck: 90m
