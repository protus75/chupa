---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- soak-run

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- 19.P4
- section 13

## Goal / Why
Author the sole terminal Phase 3 admission for Check to review and lift.

## Scope in / Scope out
Parse the YAML between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 directly from CHUPA_PLAN.md before writing. Begin admissions[27:]: phase3-exit only. Author phase3-exit as the sole payload, without a successor continuation. It starts high/high under 19.L's terminal rule and depends on phase3-continue-27, transitively covering every preceding Phase 3 payload. Do not duplicate, rename, split, omit, reorder or edit registry rows, and never seed past the next phase.

The parent checked soak-run, not the terminal. Validate the terminal now against 19.P3, not a non-exit entry unit. Resolve its governing contracts and the needed next-phase core citations from the live plan when authoring the exit's seeder role. Apply entry_unit_gap only to non-exit entries needed by that authoring, and resolve_plan_contract to the cited units and row citations, section 13 and seeder-role contracts. Missing/thin units or omitted needed facts return premise_failed, kind: spec_gap, naming the owning cited hardenable unit for section 11.4 hardening. Never invent an Owner, record shape, observable or named test, or copy unit text into a seed. The renderer supplies the cited contract.

The terminal reads the committed tickets/soak-run/daemon-soak-report.json through its artifacts schema and authors the 19.P4 core as 19.P3 and 19.L govern. Follow committed-artifact custody and transitive-dependency coverage. Read merged runner, canonical writer, artifacts schema, report purge/lift/validation, merge admission, Git/Effects and forced predecessors/direct callers. Re-grep produce/write_report, KNOWN_ARTIFACTS, Artifact, public surfaces/allowlists, absence assertions and direct callers across chupa/, eval/ and tests/. Validate only this terminal and its immediate next-phase core needs; no later admissions. The exit reads production evidence, never a report written by its own tests or manually refreshed.

Carry these merged report and custody obligations:
test_daemon_soak_command_writes_report_only_on_green, test_daemon_soak_requires_member_local_evidence, test_daemon_soak_is_rederivable, test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift, test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report, test_outbox_only_check_accepts_registered_report, test_outbox_only_admission_records_null_commit_and_retires.
Preserve report-purge, schema-validation, named-report-required, checks-only and inherited byte-equal exclusion. Journal alone writes durable events; Box alone writes queue records; ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The checks lift alone commits registered reports.

Create tests/test_seeded_phase3_27.py naming exactly phase3-exit. Pin confirmed seed birth (later rejection is lifecycle history), high/high start, exact dependencies and budgets bounded by drain.max_ticket_minutes, terminal suffix and sole-payload identity within seeding.max_seeds_per_admission, citation roles, named obligations/custody and earned closure with path-specific reasons. Record the authoring head, merged idiom blob, file/ticket sizes and plan-unit lengths IN that test. Its context closure and maximum-effort base render use fixed authoring snapshots, never live sizes or live plan lengths. Use the named assertions test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots and test_payloads_run_preservation_suites_without_fencing_or_embedding_them as applicable to a terminal with no successor.

The registry floor is tickets, tests/test_phase3_exit.py and tests/test_seeded_phase4_core.py. Earn any additions only through 19.L rules 2-5 or cited seam-owner closure, recording exact paths and reasons in the batch test. No signature change or extra fence is presumed. Existing fenced paths are Context by default; On-demand needs measured embedding beyond 300,000-character headroom. Created paths, including same-admission siblings, belong in neither partition. Exclude prompt-specs and delimiter-bearing files from Context. Unchanged preservation suites run in Verification without fencing or embedding. Only tests/test_seeded_phase3_core.py is the merged earlier idiom; never embed tests/test_seeded_phase3_25.py, tests/test_seeded_phase3_26.py or the new test. Keep serve's normal merged-path partition and historical seeding snapshots intact.

Keep previously approved seeds verbatim while bytes match ticket_sha; re-author only snagged seeds. Leave the new terminal seed uncommitted for Check's requisition_review. Check records approve in tickets/phase3-continue-27/checks.json before one chupa(phase3-continue-27): seeds ticket-plane commit. Commit only the new batch test. Out: Box messages, plan edits, existing tickets/run records, historical tests, ticket paths in the code commit, later implementation, manual HGATE release, verification filtering and invented records.

## Scope fence
- tickets
- tests/test_seeded_phase3_27.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_27.py` exits 0 proving sole terminal identity, confirmed birth, lint, transitive edges, high/high start and drain-bounded budgets.
2. `uv run pytest -q tests/test_seeded_phase3_27.py` exits 0 pinning terminal citation roles, named obligations/custody, earned closure and fixed-snapshot render feasibility.
3. `tickets/phase3-continue-27/checks.json` records requisition_review approve for phase3-exit before the single seed lift; the seed stays uncommitted and only the new test is committed.
4. `uv run pytest -q` exits 0 with production behavior unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_27.py
uv run pytest -q
```

## Definition of rejected
A missing needed contract fact returns premise_failed, kind: spec_gap, naming its governing cited hardenable unit for section 11.4 hardening. A forced path beyond an earned fence returns premise_failed; never invent or widen the contract.

## Time budget
- expected: 60m
- stuck: 90m
