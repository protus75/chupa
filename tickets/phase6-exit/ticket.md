---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase6-continue-08
- exit-receipt-machinery

## Context
- eval/host_loop.py
- chupa/artifacts.py
- chupa/git.py
- tickets/go-grade-run/review-baseline-report.json

## Plan contract
- 19.L
- 19.I
- 19.P6
- 19.P6.exit-receipt-machinery
- 19.P6.fixture-host-scaffold
- 19.P6.supervised-merge-hold
- 19.P6.go-grade-machinery
- 19.P6.go-grade-run

## Goal / Why
Read the terminal Phase 6 evidence and produce its deterministic receipt through Check.

## Scope in / Scope out
Position 8 carries admissions[8:]: [phase6-exit], the sole terminal payload. KNOWN-HARD high/high starts under 19.L's phase-exit tier law. No successor, no seeds, no next phase, no GO recording and no live journal read.

Create only tests/test_phase6_exit.py. Run the merged eval.host_loop harness as producer after exit-receipt-machinery merges. The machinery owns HostLoopReport and ExitReceipt in chupa/artifacts.py, HOST_LOOP_REPORT and EXIT_RECEIPT registrations in chupa/stages.py, and eval.host_loop.write_report/write_receipt as canonical writers. Check purges registered outputs before Verification: run the harness command FIRST. Read the reports at their repo-relative paths, the fresh OUTBOX copies at Check and lifted copies on merged main. Missing files fail closed, never skip. Leave both reports uncommitted for Check's schema-validating ticket-plane lift.

Read the committed go-grade-run baseline through the existing reader. go-grade-machinery owns ReviewBaselineReport, REVIEW_BASELINE_REPORT registration and eval.harness's canonical writer; go-grade-run is its producer. Complete and measured partial NO_GO are valid evidence. Preserve the actual embedded verdict_signal identity; never fabricate journal identity or approval provenance.

Before implementation resolve required_units and resolve_plan_contract for all citations and check entry_unit_gap. The terminal contract lives in 19.P6's exit reads and RECEIPT and 19.L's TERMINAL provision, with no invented exit entry. Missing or contradictory owning facts return premise_failed, kind: spec_gap naming the owning unit.

Exit tests read produced report entries. Unchanged machinery preservation tests own disposable member-local journal, squash-trailer and regression-gate proof. Do not reopen deleted fixture checkouts or run serve inside exit tests. Regeneration consumes report bytes at the declared paths and the committed baseline, with no git-HEAD read of this exit's own reports. No production changes, manual report commits, Box messages, release, cutover or live-host soak.

## Scope fence
- tickets/phase6-exit/host-loop-report.json
- tickets/phase6-exit/exit-receipt.json
- tests/test_phase6_exit.py

## Acceptance criteria
1. `uv run pytest -q tests/test_phase6_exit.py` passes with test_phase6_exit_transitive_dependencies reading committed tickets and Git.first_parent_squashes trailers to prove transitive Phase 6 coverage of core-renderer, core-drift-classifier, core-drift-activation, migrate-config, host-contract-doc, fixture-host-scaffold, bug-gate-grammar, report-inbox-triage, escape-column, supervised-merge-hold, go-grade-machinery, go-grade-run and exit-receipt-machinery. Code payloads have merged squash trailers; the no-code go-grade-run is covered by its committed baseline report and dependency chain, without requiring a nonexistent code squash. Read merged presence only, never checks.json or approval provenance or live journal.
2. `uv run pytest -q tests/test_phase6_exit.py` passes with test_phase6_exit_machine_ticket_merge reading tickets/phase6-exit/host-loop-report.json (HOST_LOOP_REPORT; machinery exit-receipt-machinery, producer phase6-exit's harness run). Validate at least three ordered machine_ticket_merge entries, distinct producing_run identities, expected/observed machine_ticket_merged, empty engine_plane_edits and auditor, green true, and the matching pass read in tickets/phase6-exit/exit-receipt.json.
3. `uv run pytest -q tests/test_phase6_exit.py` passes with test_phase6_exit_report_to_regression_bug_loop reading the report_to_regression_bug_loop entry in tickets/phase6-exit/host-loop-report.json (HOST_LOOP_REPORT; machinery exit-receipt-machinery, producer phase6-exit's harness run). Pin producing_run, expected/observed report_replayed_regression_bug_merged, empty engine_plane_edits and auditor, green true, and the corresponding pass receipt read. The real head-pass/base-defect regression-gate proof remains in the unchanged machinery tests.
4. `uv run pytest -q tests/test_phase6_exit.py` passes with test_phase6_exit_escape_attribution reading the escape_attribution entry in tickets/phase6-exit/host-loop-report.json (HOST_LOOP_REPORT; machinery exit-receipt-machinery, producer phase6-exit's harness run). Pin producing_run, expected/observed escape_attributed_by_squash_trailers, empty engine_plane_edits and auditor, green true, and the corresponding pass receipt read. Member-local trailer proof remains in the unchanged machinery tests.
5. `uv run pytest -q tests/test_phase6_exit.py` passes with test_phase6_exit_go_grade_report reading tickets/go-grade-run/review-baseline-report.json (REVIEW_BASELINE_REPORT; machinery go-grade-machinery, producer go-grade-run). Validate its go_grade_report pass receipt read and unchanged actual embedded verdict_signal identity. Complete and partial NO_GO are accepted; invalid baseline and partial GO refuse. Never record GO.
6. `uv run pytest -q tests/test_phase6_exit.py` passes with test_phase6_exit_receipt_regeneration reading tickets/phase6-exit/host-loop-report.json and tickets/phase6-exit/exit-receipt.json at the declared paths (HOST_LOOP_REPORT and EXIT_RECEIPT; machinery exit-receipt-machinery, producer phase6-exit's harness run). Validate every read verdict and both exact input-byte digests against the committed baseline. eval.host_loop.regenerate and canonical reproduce the receipt bytes identically without a state directory or live journal access and without a git-HEAD read of the exit's own reports. Missing, red or invalid evidence fails closed.
7. The commands `uv run pytest -q tests/test_host_loop.py`, `uv run pytest -q tests/test_stages.py` and `uv run pytest -q tests/test_gates.py` preserve unchanged machinery obligations remain green in Verification: tests/test_host_loop.py::test_exit_receipt_entry_unit, tests/test_host_loop.py::test_host_loop_closed_schema, tests/test_host_loop.py::test_host_loop_drives_supervised_fixture_serve, tests/test_host_loop.py::test_host_loop_report_regression_and_escape, tests/test_host_loop.py::test_host_loop_requires_member_auditor_green, tests/test_host_loop.py::test_exit_receipt_closed_schema_and_baseline_identity, tests/test_host_loop.py::test_exit_receipt_regenerates_from_committed_bytes, tests/test_stages.py::test_host_loop_and_receipt_registered_checks_lift and tests/test_gates.py::test_host_loop_regression_uses_real_bug_gate.
8. `uv run pytest -q` and all Verification commands pass with historical fixtures unchanged; reports stay uncommitted for Check's schema-validating lift. No seeds or next phase are authored.

## Verification
```
uv run python -m eval.host_loop --out tickets/phase6-exit/host-loop-report.json --receipt tickets/phase6-exit/exit-receipt.json --baseline tickets/go-grade-run/review-baseline-report.json
uv run pytest -q tests/test_phase6_exit.py
uv run pytest -q tests/test_host_loop.py
uv run pytest -q tests/test_stages.py
uv run pytest -q tests/test_gates.py
uv run pytest -q tests/test_fixture_host.py tests/test_bug_gate.py tests/test_inbox.py tests/test_triage.py tests/test_supervised_merge_hold.py tests/test_merge.py tests/test_seed_path.py
uv run pytest tests/test_eval_harness.py tests/test_go_grade.py tests/test_stages.py tests/test_merge.py
uv run pytest -q tests/test_watchdog_activation.py::test_eval_owned_budgets_preserve_synthetic_identities
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
An unmet exit read returns premise_failed naming it. Missing or contradictory entry facts return premise_failed, kind: spec_gap naming the owning unit. Criteria-forced changes beyond this fence require plan repair.

## Time budget
- expected: 60m
- stuck: 90m
