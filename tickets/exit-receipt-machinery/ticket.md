---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue-07
- go-grade-run

## Context
- chupa/artifacts.py
- chupa/stages.py
- tests/test_gates.py
- tests/test_stages.py
- tests/test_fixture_host.py
- hosts/fixture/CLAUDE.md
- hosts/fixture/README.md
- hosts/fixture/app.py
- hosts/fixture/bin/claude
- hosts/fixture/bin/pnpm
- hosts/fixture/check.py
- hosts/fixture/config.yaml
- hosts/fixture/evidence/escape.json
- hosts/fixture/evidence/escape.log
- hosts/fixture/evidence/merge-add.json
- hosts/fixture/evidence/merge-add.log
- hosts/fixture/evidence/merge-bonus.json
- hosts/fixture/evidence/merge-bonus.log
- hosts/fixture/evidence/merge-floor.json
- hosts/fixture/evidence/merge-floor.log
- hosts/fixture/evidence/regression.json
- hosts/fixture/evidence/regression.log
- hosts/fixture/regression_test.py
- hosts/fixture/replay.py
- hosts/fixture/reports/escape.json
- hosts/fixture/reports/merge-add.json
- hosts/fixture/reports/merge-bonus.json
- hosts/fixture/reports/merge-floor.json
- hosts/fixture/reports/regression.json
- hosts/fixture/scaffold.py
- hosts/fixture/scripts.json
- hosts/fixture/settings.json
- chupa/seams.py
- chupa/git.py
- tests/test_inbox.py

## Plan contract
- 19.I
- 19.P6.exit-receipt-machinery
- 19.P6.fixture-host-scaffold
- 19.P6.supervised-merge-hold
- 19.P6.go-grade-machinery
- 19.P6.go-grade-run

## Goal / Why
Build a supervised fixture runner and validated deterministic report writers that the terminal exit can run through Check.

## Scope in / Scope out
Implement the registry machinery under its cited entry. New eval/host_loop.py owns the runner and both canonical writers; chupa/artifacts.py owns the schemas and constants, and chupa/stages.py owns registration and checks-lift custody. Read the cited entries for all record shapes, evidence requirements and refusal cases. This machinery tests production but does not lift its own reports; phase6-exit is the later producer.

Use the merged supervised serve subprocess, control-inbox identities, scripted adapter, report consumer, bug gate and squash-trailer reader. Read chupa/serve.py, chupa/control.py, chupa/audit.py, chupa/triage.py and chupa/gates.py before composing the runner. Inject the existing clock, process, filesystem and notification seams; bound waits and clean up process groups on every exit. Machine actors confirm only this disposable fixture's drafts and candidates, with no cap re-arm or GO recording. Derive every member observation from its own production evidence and require its invariant audit to pass. Missing evidence or a failed member must exit nonzero with the unmet read.

Add only fixture support needed for this loop. The regression must be kind: bug with a Regression command and a carries prefix matching a branch-changed test/fixture path. Its test must already exist on the defective base; the overlay must preserve the defect and emit the regression_result JSON protocol. Keep durable report evidence in the authored bug's evidence directory. Preserve the scaffold's deterministic replay, closed scenarios, zero-cost adapter and disposable-write boundary.

The 19.L contradicted-test closure adds tests/test_fixture_host.py to the registry fence. Migrate only predecessor assertions contradicted by the real bug-gate shape, in the same commit: test_fixture_scenario_list_is_closed's settings-only edit vocabulary, settings-only scope fence and exact row keys; test_fixture_regression_exists_at_base's settings-only diff_names; and test_fixture_profile_loads's exact engine_plane_safety_inventory. Preserve base-test presence, genuine defect failure and fixed-head success. Run the migrated assertions in Verification. Do not weaken the production bug gate or migrate historical seeding fixtures.

Before implementation, test required_units, resolve_plan_contract and entry_unit_gap for every cited non-exit entry, including the successor's terminal contract closure. Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning unit. Use the terminal role contract in the phase unit and build laws, not an invented phase6-exit entry.

Receipt regeneration consumes only validated committed input bytes and preserves the baseline's actual embedded identity, including complete or partial NO_GO. No live journal is needed for regeneration. No new configuration, signal, frontmatter, host cutover, live-host soak, seed emission, manual evidence commit or production change outside this fence is part of this deliverable.

Migrate tests/test_inbox.py::test_report_replay_to_regression to consume the migrated bug fixture instead of appending its own Regression section, keeping its report-custody and regression-overlay proofs.

## Scope fence
- chupa/artifacts.py
- chupa/stages.py
- eval/host_loop.py
- tests/test_host_loop.py
- tests/test_gates.py
- tests/test_stages.py
- hosts/fixture/
- tests/test_fixture_host.py
- tests/test_inbox.py

## Acceptance criteria
1. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_exit_receipt_entry_unit proving required_units, unique resolve_plan_contract, all four entry_unit_gap parts and missing-part refusal, including successor-contract closure before seed writes.
2. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_host_loop_closed_schema rejecting extra keys, reordered members, repeated merge-run identities, inconsistent observations/green and green entries with auditor findings or engine edits.
3. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_host_loop_drives_supervised_fixture_serve exercising real subprocess composition, machine-actor draft and held confirms, three distinct production merges without engine edits, and cleanup after timeout or failure.
4. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_host_loop_report_regression_and_escape proving report ingestion and replay into a real regression-gated bug and trailer-derived escape attribution, each from member-local evidence.
5. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_host_loop_requires_member_auditor_green refusing absent evidence and red member audits.
6. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_exit_receipt_closed_schema_and_baseline_identity covering every read verdict, digest validation, unknown keys, actual unchanged signal identity, complete GO and NO_GO, partial NO_GO and partial GO rejection.
7. `uv run pytest -q tests/test_host_loop.py` passes with tests/test_host_loop.py::test_exit_receipt_regenerates_from_committed_bytes proving exact input-byte hashes and identical regenerated receipt bytes without state-directory access.
8. `uv run pytest -q tests/test_stages.py` passes with tests/test_stages.py::test_host_loop_and_receipt_registered_checks_lift covering both registrations, output purge before Verification, mandatory named outputs, schema refusal, sole checks-lift custody and no machinery self-lift.
9. `uv run pytest -q tests/test_gates.py` passes with tests/test_gates.py::test_host_loop_regression_uses_real_bug_gate proving head success and defective merge-base failure with carries overlay; a missing base test cannot establish the defect.
10. `uv run pytest -q tests/test_fixture_host.py` passes with the migrated test_fixture_scenario_list_is_closed, test_fixture_regression_exists_at_base and test_fixture_profile_loads assertions proving the bug-gate fixture shape while retaining unrelated scaffold behavior.
11. `uv run pytest -q` and all preservation commands pass with historical fixtures unchanged and plan lint green.

## Verification
```
uv run pytest -q tests/test_host_loop.py
uv run pytest -q tests/test_gates.py
uv run pytest -q tests/test_stages.py
uv run pytest -q tests/test_fixture_host.py
uv run pytest -q tests/test_bug_gate.py tests/test_inbox.py tests/test_triage.py tests/test_supervised_merge_hold.py tests/test_merge.py tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory owning facts return premise_failed with kind: spec_gap and the owning unit. A criteria-forced path beyond earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
