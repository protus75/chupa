---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- outbox-only-admission

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.daemon-soak
- 19.P3.daemon-soak-runner

## Goal / Why
Author the daemon-soak admission and its continuation for Check to review and lift.

## Scope in / Scope out
Parse the YAML between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 directly from CHUPA_PLAN.md before writing; admissions[24:] is the live suffix. Author only daemon-soak and phase3-continue-25. The deep payload starts high/high, depends on phase3-continue-24, and cites exactly 19.I and 19.P3.daemon-soak (the row has no additional cite). The successor starts medium/medium, depends on daemon-soak and begins admissions[25:]. Do not author daemon-soak-runner or any later payload here.

Run entry_unit_gap and resolve_plan_contract for this admission, row citations, section 13 and needed next-seeder citations at the authoring head. Validate the immediate lookahead 19.P3.daemon-soak-runner before authoring; only the current admission and immediate successor lookahead require validation, never later units. The parent checked daemon-soak, not this lookahead. A missing/thin unit or omitted needed fact returns premise_failed with kind: spec_gap and that unit for section 11.4 hardening. All Phase 3 rows are hardenable. Never guess an Owner, record shape, observable or named test.

The renderer injects Owner, Records, Observable and Tests; never copy unit text into a seed. Preserve exact own-entry/row citations and all named invariant obligations and record custody. For daemon-soak pin through 19.P3.daemon-soak: test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift. Its implementing Verification is `uv run pytest tests/test_daemon_soak.py tests/test_stages.py`. Preserve the named report-purge, schema-validation, named-report-required, checks-only custody and inherited byte-equal exclusion predecessors. Its schema, provenance, strict ordered membership, false-green refusal, filesystem writer, registration and no machinery-produced exit report stay governed by that entry; it supplies neither runner nor producing run.

Read merged artifacts, stages, report writer precedents, Git/Effects, merged runner, daemon, CLI run/drain and build_daemon_core, serve composition, Journal, Restart, Timers, the production-composition harness and every predecessor/direct caller forced by the path. The registry floor is eval/daemon_soak.py, chupa/artifacts.py, chupa/stages.py and tests/test_daemon_soak.py. Re-grep KNOWN_ARTIFACTS, Artifact, report purge/lift and validation, public surfaces and allowlists, production absence assertions and direct callers across chupa/, eval/ and tests/. Earn additions only through 19.L rules 2-5 or cited seam-owner closure; record each exact path, reason and existing-path Context/on-demand partition in the new batch test. Preserve every floor; no signature change or extra fence is presumed from lookahead.

Keep sole-writer custody: Journal writes durable events, Box queue records, ControlInbox control decisions. Journal(state_dir, clock) and append/read/close signatures, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup stay intact. The existing checks lift alone commits registered reports. Production evidence uses injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers, the real CLI/async serve entrypoint and merged production-composition harness when applicable. No test-only graph, live host work, real-model calls, wall-clock waits, notify transport or routing changes.

Existing fenced paths are Context by default. On-demand requires measured embedding beyond 300,000-character headroom. Created paths belong in neither partition, including same-admission sibling creations. Exclude prompt-specs and delimiter-bearing sources from Context. Unchanged preservation suites run in Verification only, neither fenced nor embedded, except registry floors retain their fence and existing-path partition. Serve follows the normal merged-path partition; never migrate historical seeding snapshots.

Create phase3-continue-25 with the exact seeder-role Plan contract from 19.L and section 13: 19.L, 19.I, 19.P3, section 13, 19.P3.daemon-soak-runner and its live row citations, plus the needed immediate lookahead 19.P3.soak-run. Its fence is tickets and tests/test_seeded_phase3_25.py; embed tests/test_seeded_phase3_core.py as its merged earlier idiom, never this admission's test. It authors daemon-soak-runner and phase3-continue-26, the latter starting admissions[26:], only after its own needed-unit validation. Carry cite-don't-copy, closure greps, named invariant obligations and record custody with the sole writers forward.

Create tests/test_seeded_phase3_24.py naming exactly daemon-soak and phase3-continue-25. Required tests are test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots and test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Pin confirmed seed birth (later rejection is lifecycle history), dependencies, starts, budgets, exact citations, earned closure/reasons, named tests/custody through governing citations and successor roles. Record authoring head, merged idiom blob, file and ticket sizes and plan-unit lengths IN that test. Context closure and maximum-effort base render use fixed authoring snapshots, never live sizes or live plan lengths. Embed only the merged core idiom, never tests/test_seeded_phase3_23.py or tests/test_seeded_phase3_24.py. Every stuck budget fits drain.max_ticket_minutes.

Each continuation emits only the next admission and successor, within seeding.max_seeds_per_admission including the tail, depending on every preceding payload. Deep rows start high/high; other rows medium/medium. Terminal phase3-exit is its sole payload without a successor; never seed past the next phase. Do not duplicate, rename, split, omit, reorder or edit registry rows.

Keep previously approved seeds verbatim while bytes match ticket_sha; re-author only snagged seeds. Leave both new seeds uncommitted for Check's requisition_review. Check records approve for both in tickets/phase3-continue-24/checks.json and lifts them together through one chupa(phase3-continue-24): seeds ticket-plane commit. Commit only the new test. Out: Suggestion Box messages, plan/registry edits, existing tickets/run records, historical tests, ticket paths in the code commit, later implementation, manual HGATE release, verification filtering and invented records.

## Scope fence
- tickets
- tests/test_seeded_phase3_24.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_24.py` exits 0 over exactly daemon-soak and phase3-continue-25, proving confirmed birth, intake lint, dependencies, starts and drain-bounded budgets.
2. `uv run pytest -q tests/test_seeded_phase3_24.py` exits 0 pinning exact citations, named obligations/custody, earned closure and fixed-snapshot render feasibility.
3. `tickets/phase3-continue-24/checks.json` records requisition_review approve for both before one ticket-plane seed lift; seed files stay uncommitted and only the new test is committed.
4. `uv run pytest -q` exits 0 with production behavior unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_24.py
uv run pytest -q
```

## Definition of rejected
A needed governing entry missing a fact or contradicting merged behavior returns premise_failed, kind: spec_gap, naming that unit for section 11.4 hardening. A forced file beyond an earned fence returns premise_failed; do not invent a contract or widen scope while implementing.

## Time budget
- expected: 60m
- stuck: 90m
