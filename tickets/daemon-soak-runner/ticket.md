---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-25

## Context
- eval/daemon_soak.py
- tests/test_daemon_soak.py
- chupa/artifacts.py
- chupa/stages.py
- chupa/git.py
- chupa/effects.py
- chupa/seams.py
- chupa/runner.py
- chupa/daemon.py
- chupa/__main__.py
- chupa/serve.py
- chupa/journal.py
- chupa/restart.py
- chupa/timers.py
- chupa/box.py
- chupa/audit.py
- chupa/rework.py
- chupa/mergequeue.py
- chupa/reconcile.py
- chupa/control.py
- eval/shakeout/run.py

## Plan contract
- 19.I
- 19.P3.daemon-soak-runner

## Goal / Why
A bounded deterministic invocation derives the closed soak report from production serve evidence and returns it to the existing writer.

## Scope in / Scope out
Implement the runner and command governed by 19.P3.daemon-soak-runner; its injected Owner, Records, Observable and Tests supply the contract. Keep the canonical write_report implementation and its schema/registration intact. Public produce returns evidence to that writer; this machinery produces no exit report for its own lift. The later soak-run supplies the separate producing run.

Exercise the real CLI/async serve entrypoint and merged production-composition harness through injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers. Drive real dispatch and result consumption. Harness fixture setup stays in the runner module, with no imports from tests. Read the production-composition harness on disk before implementation. Preserve the engine algorithms and use their existing operations; there are no earned fence additions or signature changes. Re-grep produce/write_report, KNOWN_ARTIFACTS, Artifact, report purge/lift/validation, public surfaces/allowlists, production absence assertions and direct callers across chupa/, eval/ and tests/ before writing. Read chupa/merge.py, chupa/drain.py, chupa/scheduler.py, chupa/watcher.py and forced predecessor/direct callers on disk as well as Context.

The entry citation owns strict membership, per-member production evidence, recurring cycles, false-green refusal, cleanup, byte-identical re-derivation and source-HEAD provenance. Read original-run recovery alerts, both conflict rungs and integration-red refusal from member-local evidence. Use audit_journal on the entire member-local history and the existing Box fault-visibility seam. Do not supply success records, auditor verdicts or gate/admission/reconcile answers. The sole command form is uv run python -m eval.daemon_soak --out <path>; no selector or additional mode. Preserve report-purge, schema-validation, named-report-required, checks-only custody and inherited byte-equal exclusion predecessors.

Journal alone writes durable events; Box alone writes queue records; ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The checks lift alone commits registered reports.

Named runner and command obligations through the entry: test_daemon_soak_runs_production_serve, test_daemon_soak_advances_each_member_24_hours, test_daemon_soak_worker_recovery, test_daemon_soak_conflict_rungs, test_daemon_soak_semantic_red_preserves_main, test_daemon_soak_requires_member_local_evidence, test_daemon_soak_cleans_up_owned_lifetimes, test_daemon_soak_is_rederivable, test_daemon_soak_command_writes_report_only_on_green. Preserve the four merged schema/writer/lift obligations: test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift. Preserve custody predecessors: test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report. These obligations continue through their governing citations; never duplicate entry-unit prose. The unfenced tests/test_serve.py, tests/test_mergequeue.py, tests/test_reconcile.py and tests/test_audit.py are unchanged preservation suites run only in Verification, neither fenced nor embedded. The floor retains the existing writer and schema tests in Context and fences them for the new command test.

Out: live host work, real-model calls, wall-clock waits, notify transport, routing changes, second daemon graph, report commits, new records, plan changes and historical seeding tests.

## Scope fence
- eval/daemon_soak.py
- tests/test_daemon_soak.py
- tests/test_daemon_soak_runner.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_serve.py tests/test_mergequeue.py tests/test_reconcile.py tests/test_audit.py` exits 0 with the entry-named production, time advancement, recovery, conflict, integration refusal, local evidence, cleanup and re-derivation tests.
2. `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_serve.py tests/test_mergequeue.py tests/test_reconcile.py tests/test_audit.py` exits 0 including test_daemon_soak_command_writes_report_only_on_green, proving canonical writer use, provenance and failed-member no-write refusal.
3. `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_serve.py tests/test_mergequeue.py tests/test_reconcile.py tests/test_audit.py` exits 0 preserving the merged schema/writer/lift and engine custody obligations; no machinery report is lifted.

## Verification
```
uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_serve.py tests/test_mergequeue.py tests/test_reconcile.py tests/test_audit.py
```

## Definition of rejected
A missing needed contract fact returns premise_failed, kind: spec_gap, naming its governing cited unit for section 11.4 hardening. A forced path beyond the earned fence returns premise_failed; never invent or widen the contract.

## Time budget
- expected: 60m
- stuck: 90m
