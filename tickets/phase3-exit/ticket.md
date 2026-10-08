---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-27

## Context
- chupa/artifacts.py
- chupa/stages.py
- chupa/merge.py
- chupa/git.py
- chupa/effects.py
- chupa/seams.py
- chupa/serve.py
- tests/test_seeded_phase3_core.py
- tickets/soak-run/daemon-soak-report.json

## Plan contract
- 19.L
- 19.I
- 19.P3
- 19.P4
- 19.P4.watchdog-event-stream
- 19.P4.notify-transport
- section 6
- section 9
- section 13
- section 15

## Goal / Why
Prove the Phase 3 exit from committed production evidence and admit the Phase 4 core.

## Scope in / Scope out
This is the sole terminal payload of the Phase 3 registry. Start high/high because 19.L names phase exits known-hard. The predecessor edge covers soak-run and every preceding Phase 3 payload transitively. In tests/test_phase3_exit.py, name test_phase3_exit_dependency_coverage for that graph coverage, and test_phase3_exit_reads_committed_soak_report for the report read. The dependency graph is the merged-presence proof; any git read is at most the existing squash-trailer check, with no approval-provenance cross-check and no new Git operation.

Read tickets/soak-run/daemon-soak-report.json using DaemonSoakReport and DAEMON_SOAK_MEMBERS. Require all ordered members green, matching observations and empty member auditors, and retain source provenance. Machinery emitters are daemon-soak and daemon-soak-runner; the later producer is soak-run. The exit consumes their committed production output. It never calls the writer to refresh that input, creates a substitute fixture as exit evidence, or reads the gitignored live state directory. An unmet read returns premise_failed naming the member or missing artifact. No separate Phase 3 report is specified by this registry row.

Parse the next-phase registry directly from the committed plan. Author only watchdog-event-stream, notify-transport and phase4-continue from its first admission, preserving row identity and order. Use their cited entry contracts for owner, records, observables and named tests; the renderer injects those contracts. The implementing seeds cite 19.I, their own entry and row citations; both depend on phase3-exit and notify-transport also depends on watchdog-event-stream. The continuation depends on both core payloads, owns tickets plus its new tests/test_seeded_phase4_01.py, and uses the merged tests/test_seeded_phase3_core.py idiom. It names its next admission and shrinking suffix, and validates the contracts needed for that admission when it runs. Do not author later admissions here. Source is seed, birth is confirmed, ordinary starts are medium/medium, and budgets fit drain.max_ticket_minutes. Only the phase3-exit terminal starts high/high here.

Create tests/test_seeded_phase4_core.py to pin the three identities, birth, grammar, dependency edges, citation roles, earned fences, Context partitions and fixed authoring snapshots for maximum-effort renders within 300,000 characters. Validate only the immediate Phase 4 core's needed non-exit entry units with entry_unit_gap and resolve_plan_contract, including row citations and seeder-role contracts. Missing governing facts return premise_failed, kind: spec_gap, identifying the cited owning unit; never manufacture a contract or copy its text.

Before authoring, read the merged runner and canonical writer in eval/daemon_soak.py from disk (its engine delimiters exclude it from Context), artifacts registration, report purge/validation/lift, merge admission, Git/Effects, forced predecessor tickets and direct callers. Re-grep produce/write_report, KNOWN_ARTIFACTS, Artifact, public surfaces, allowlists and absence assertions across chupa/, eval/ and tests/. For the core notify production flip, inspect tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify and fence that existing test if contradicted, retaining its unrelated assertions. Earn additions only under 19.L rules 2-5 or cited seam-owner closure, with exact paths and reasons in the new batch test. No signature change is presumed. Existing fenced paths default to Context; On-demand requires measured headroom overflow. Created paths, same-admission siblings, prompt-spec sources and delimiter-bearing files never enter Context. Preserve serve's merged-path partition and historical seeding snapshots.

The following unchanged suites carry the named custody obligations:
tests/test_daemon_soak.py: test_daemon_soak_command_writes_report_only_on_green, test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift.
tests/test_daemon_soak_runner.py: test_daemon_soak_requires_member_local_evidence, test_daemon_soak_is_rederivable.
tests/test_stages.py: test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report, test_outbox_only_check_accepts_registered_report.
tests/test_merge.py: test_outbox_only_admission_records_null_commit_and_retires.

Preserve report-purge, schema-validation, named-report-required, checks-only custody and inherited byte-equal exclusion. Journal alone writes durable events; Box alone writes queue records; ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The checks lift alone commits registered reports. These suites run in Verification without being fenced or embedded.

Write new seeds directly as uncommitted ticket-plane output. Check owns requisition_review, its checks.json approvals and the single seed lift; the code commit contains only the two new tests. Approved prior seeds remain verbatim while bytes match ticket_sha; re-author only snagged seeds. Out: production changes, existing tickets/run records, live-journal reads, manually refreshed reports, Box messages, plan edits, historical tests, extra admissions, verification filtering and manual release.

## Scope fence
- tickets
- tests/test_phase3_exit.py
- tests/test_seeded_phase4_core.py

## Acceptance criteria
1. `uv run pytest -q tests/test_phase3_exit.py` exits 0 proving test_phase3_exit_dependency_coverage over every preceding Phase 3 payload and test_phase3_exit_reads_committed_soak_report over all three production members from the committed report through its schema.
2. `uv run pytest -q tests/test_seeded_phase4_core.py` exits 0 proving exactly the Phase 4 core and one continuation, confirmed seed birth, exact consumption edges, named entry obligations, earned closure and fixed-snapshot render feasibility.
3. `tickets/phase3-exit/checks.json` records requisition_review approve for each emitted seed before its single ticket-plane seeds commit; seed files stay out of the code commit.
4. `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py` and `uv run pytest tests/test_stages.py tests/test_merge.py` exit 0 preserving production evidence and lane custody.

## Verification
```
uv run pytest -q tests/test_phase3_exit.py
uv run pytest -q tests/test_seeded_phase4_core.py
uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py
uv run pytest tests/test_stages.py tests/test_merge.py
```

## Definition of rejected
An unmet committed exit read returns premise_failed naming it. Missing or contradictory governing core facts return premise_failed, kind: spec_gap, naming their cited owning hardenable unit for section 11.4. A criteria-forced path outside an earned fence returns premise_failed; never invent evidence or widen the registry.

## Time budget
- expected: 60m
- stuck: 90m
