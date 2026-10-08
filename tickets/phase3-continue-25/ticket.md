---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- daemon-soak

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.daemon-soak-runner
- 19.P3.soak-run

## Goal / Why
Author the deterministic soak runner admission and its immediate continuation for Check to review and lift.

## Scope in / Scope out
Parse the YAML between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 directly from CHUPA_PLAN.md before writing; admissions[25:] is the live suffix. Author only daemon-soak-runner and phase3-continue-26. The deep payload starts high/high, depends on phase3-continue-25 and cites exactly 19.I and 19.P3.daemon-soak-runner, plus its live row citations (currently none). The successor starts medium/medium, depends on daemon-soak-runner and begins admissions[26:]. Do not author soak-run or later payloads here.

Run entry_unit_gap and resolve_plan_contract for the current admission, row citations, section 13 and needed next-seeder citations at the authoring head. Validate immediate lookahead 19.P3.soak-run before authoring: only this admission and immediate successor lookahead require validation, never later units. The parent checked daemon-soak-runner, not soak-run. Missing/thin units and omitted needed facts return premise_failed with kind: spec_gap and that unit for section 11.4 hardening. All Phase 3 rows are hardenable. Never guess an Owner, record shape, observable or named test.

The renderer injects Owner, Records, Observable and Tests; never copy unit text into a seed. Carry exact own-entry/row citations, named invariant obligations and record custody forward. Under 19.P3.daemon-soak-runner pin test_daemon_soak_runs_production_serve, test_daemon_soak_advances_each_member_24_hours, test_daemon_soak_worker_recovery, test_daemon_soak_conflict_rungs, test_daemon_soak_semantic_red_preserves_main, test_daemon_soak_requires_member_local_evidence, test_daemon_soak_cleans_up_owned_lifetimes and test_daemon_soak_is_rederivable. tests/test_daemon_soak.py adds test_daemon_soak_command_writes_report_only_on_green. The implementing Verification is `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_serve.py tests/test_mergequeue.py tests/test_reconcile.py tests/test_audit.py`; unfenced suites are unchanged preservation suites, neither fenced nor embedded. Preserve the four merged daemon-soak schema/writer/lift obligations without replacing the writer.

The governing entry owns public produce, the sole command form, per-member production evidence and recurring cycles, strict membership, false-green refusal, cleanup, re-derivation and provenance. Drive merged production serve through real dispatch/result consumption, with original-run recovery alerts, both conflict rungs and integration-red refusal derived from member-local evidence. Use the member-local auditor and existing Box fault visibility; never supply success records or auditor verdicts. This machinery returns its report to the canonical writer and emits no exit report for its own lift; the separate soak-run is the producer. Preserve report-purge, schema-validation, named-report-required, checks-only custody and inherited byte-equal exclusion predecessors, naming their merged tests in the authored seed.

Read merged artifacts, stages, canonical writer and report writer precedents, Git/Effects, runner, daemon, CLI run/drain and build_daemon_core, serve composition, Journal, Restart, Timers, Box, auditor, Rework, admission queue and the production-composition harness, plus every predecessor/direct caller forced by the path. The registry floor is eval/daemon_soak.py, tests/test_daemon_soak.py and tests/test_daemon_soak_runner.py. Re-grep public produce/write_report surfaces, KNOWN_ARTIFACTS, Artifact, report purge/lift and validation, public surfaces/allowlists, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn additions only through 19.L rules 2-5 or cited seam-owner closure. Record each exact path, reason and existing-path Context/on-demand partition in the new batch test. Keep every floor; no signature change or additional fence is presumed from lookahead.

Journal alone writes durable events, Box alone writes queue records and ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close signatures, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The checks lift alone commits registered reports. Production evidence uses injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers, the real CLI/async serve entrypoint and merged production-composition harness. No test-only graph, live host work, real-model calls, wall-clock waits, notify transport or routing changes.

Existing fenced paths are Context by default. On-demand requires measured embedding beyond 300,000-character headroom. Created paths belong in neither partition, including same-admission sibling creations. Exclude prompt-specs and delimiter-bearing sources from Context. Unchanged preservation suites run in Verification only, neither fenced nor embedded, except registry floors keep their fence and existing-path partition. Serve follows the normal merged-path partition; never migrate historical seeding snapshots.

Create phase3-continue-26 with the seeder-role Plan contract from 19.L and section 13, citing the phase, its next admission 19.P3.soak-run and live row citations, and needed immediate terminal lookahead governed by 19.P3. Its fence is tickets and tests/test_seeded_phase3_26.py; embed tests/test_seeded_phase3_core.py as the merged earlier idiom. It authors only soak-run and phase3-continue-27, the latter beginning admissions[27:], after its own needed-unit validation. Carry cite-don't-copy, closure greps, named invariant obligations and record custody with the sole writers forward.

Create tests/test_seeded_phase3_25.py naming exactly daemon-soak-runner and phase3-continue-26. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots and test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Pin confirmed seed birth (later rejection is lifecycle history), dependencies, starts, budgets, exact citations, earned closure/reasons, named tests/custody through governing citations and successor roles. Record authoring head, merged idiom blob, file and ticket sizes and plan-unit lengths IN that test. Context closure and maximum-effort base render use fixed authoring snapshots, never live sizes or live plan lengths. Embed only the merged core idiom, never tests/test_seeded_phase3_24.py or tests/test_seeded_phase3_25.py. Every stuck budget fits drain.max_ticket_minutes.

Each continuation emits only its next admission and successor within seeding.max_seeds_per_admission including the tail, depending on every preceding payload. Deep rows start high/high; other rows medium/medium. Terminal phase3-exit is its sole payload without a successor; never seed past the next phase. Do not duplicate, rename, split, omit, reorder or edit registry rows.

Keep previously approved seeds verbatim while bytes match ticket_sha; re-author only snagged seeds. Leave both new seeds uncommitted for Check's requisition_review. Check records approve for both in tickets/phase3-continue-25/checks.json and lifts them together through one chupa(phase3-continue-25): seeds ticket-plane commit. Commit only the new test. Out: Suggestion Box messages, plan/registry edits, existing tickets/run records, historical tests, ticket paths in the code commit, later implementation, manual HGATE release, verification filtering and invented records.

## Scope fence
- tickets
- tests/test_seeded_phase3_25.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_25.py` exits 0 over exactly daemon-soak-runner and phase3-continue-26, proving confirmed birth, intake lint, dependencies, starts and drain-bounded budgets.
2. `uv run pytest -q tests/test_seeded_phase3_25.py` exits 0 pinning exact citations, named obligations/custody, earned closure and fixed-snapshot render feasibility.
3. `tickets/phase3-continue-25/checks.json` records requisition_review approve for both before one ticket-plane seed lift; seeds remain uncommitted and only the new test is committed.
4. `uv run pytest -q` exits 0 with production behavior unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_25.py
uv run pytest -q
```

## Definition of rejected
A needed entry missing a fact or contradicting merged behavior returns premise_failed, kind: spec_gap, naming that unit for section 11.4 hardening. A forced file beyond an earned fence returns premise_failed; never invent the contract or widen scope.

## Time budget
- expected: 60m
- stuck: 90m
