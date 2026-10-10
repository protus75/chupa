---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase6-continue-05
- escape-column

## Context
- chupa/restart.py
- chupa/reconcile.py
- chupa/baseline.py
- tests/test_baseline.py
- chupa/control.py
- tests/test_control_cli.py
- tests/test_reconcile.py
- tests/test_daemon_soak_runner.py
- chupa/mergequeue.py
- tests/test_control.py
- chupa/__main__.py
- chupa/merge.py
- chupa/serve.py
- chupa/daemon.py
- tests/test_cli.py

## On-demand
- chupa/stages.py
- chupa/drain.py
- chupa/runner.py
- eval/daemon_soak.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_serve.py
- tests/test_restart_timers.py
- tests/test_drain.py

## Plan contract
- 19.I
- 19.P6.supervised-merge-hold
- section 9
- section 12

## Goal / Why
Keep a green daemon candidate in durable supervised custody until its exact admission is authorized.

## Scope in / Scope out
Implement the supervised-merge-hold registry row under its cited entry. This is the lone deep: true row in its admission and starts high/high. Read every On-demand path before editing it; the soak source is read directly because it contains engine delimiters.

Use the existing owners and injectable seams identified by the contract. Fence additions cover TicketWriter delivery/settlement, retained-run reconciliation, the admission vocabulary assertion, and the orphan assertion. Keep external callers of existing operations valid; record any criteria-forced closure wall as premise_failed rather than widening further.

Build the complete hold and its identity-bound release together. Retain approving Review evidence across clean rebases and use real daemon composition for supervision and delivery. Read the entry's Records, Observable and Tests as the detailed contract for each named obligation below. Each named test must cover every case assigned to it there. Bootstrap and foreground remain exempt; ordinary draft, Reject, pause/resume/kill and failure behavior remain covered by their existing suites. Standalone queue callers retain their existing invocation contract; daemon composition selects supervision.

No GO-grade harness, host-loop report producer, new modules, config keys, journal vocabulary, or artifact registration is part of this row. No host cutover, ticket authoring, or manual release in this implementation.

## Scope fence
- chupa/merge.py
- chupa/mergequeue.py
- chupa/serve.py
- chupa/restart.py
- chupa/baseline.py
- chupa/control.py
- chupa/__main__.py
- chupa/stages.py
- chupa/drain.py
- chupa/runner.py
- eval/daemon_soak.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_serve.py
- tests/test_restart_timers.py
- tests/test_baseline.py
- tests/test_control_cli.py
- tests/test_cli.py
- tests/test_drain.py
- tests/test_daemon_soak_runner.py
- tests/test_supervised_merge_hold.py
- chupa/daemon.py
- chupa/reconcile.py
- tests/test_control.py
- tests/test_reconcile.py

## Acceptance criteria
1. `uv run pytest -q` passes with `tests/test_supervised_merge_hold.py::test_supervised_hold_entry_unit` covering required_units, unique resolve_plan_contract resolution, and every entry_unit_gap part.
2. `uv run pytest -q` passes with `tests/test_supervised_merge_hold.py::test_hold_after_green_before_main_mutation` covering all baseline refusal cases, safety/integration ordering, and gate-red refusal.
3. `uv run pytest -q` passes with `tests/test_supervised_merge_hold.py::test_go_coverage_uses_actual_review_identity` covering served identity, tier coverage, contradictory evidence, and later GO.
4. `uv run pytest -q` passes with `tests/test_supervised_merge_hold.py::test_held_run_keeps_worktree_and_has_no_terminal` covering typed hold, stable vocabularies, retained custody, and no failure/cap path.
5. `uv run pytest -q` passes with `tests/test_serve.py::test_supervised_hold_allows_other_work` covering unrelated work and heartbeat progress, backpressure, exclusion, and result identity.
6. `uv run pytest -q` passes with `tests/test_mergequeue.py::test_supervised_confirm_regates_moved_main` covering unchanged/moved bases, two candidates, clean approval carry, conflicts, red gates, and trees.
7. `uv run pytest -q` passes with `tests/test_control.py::test_supervised_request_identity_and_replay` covering request/decision closure, stale identities, replay, duplicates, and both crash boundaries.
8. `uv run pytest -q` passes with `tests/test_control_cli.py::test_confirm_held_without_writer_lock` covering live and dirless publication, writer-lock independence, and draft/Reject preservation.
9. `uv run pytest -q` passes with `tests/test_control_cli.py::test_reject_held_candidate` covering rejection, dependency notification, no cap re-arm, and unchanged main.
10. `uv run pytest -q` passes with `tests/test_restart_timers.py::test_restart_reconstructs_supervised_admission` covering completed/partial receipts, releases across crashes, corrupt evidence, and repeated recovery.
11. `uv run pytest -q` passes with `tests/test_reconcile.py::test_live_hold_is_not_an_orphan` covering retained held ownership, no model rerun, incomplete intents, and ordinary orphan handling.
12. `uv run pytest -q` passes with `tests/test_merge.py::test_foreground_admission_never_supervised_holds` covering foreground exemption through its actual composition.
13. `uv run pytest -q` passes with `tests/test_drain.py::test_bootstrap_never_supervised_holds` covering bootstrap exemption through its actual composition.
14. `uv run pytest -q` passes with `tests/test_daemon_soak_runner.py::test_soak_uses_candidate_base_regate_receipt` covering real served identity, operator fixture confirms, moved base, and member-local audit.
15. `uv run pytest -q` and the preservation commands pass; the plan stays lint-green and the historical seeding fixtures are unchanged.

## Verification
```
uv run pytest -q tests/test_supervised_merge_hold.py
uv run pytest -q tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_restart_timers.py tests/test_baseline.py tests/test_control.py tests/test_control_cli.py tests/test_cli.py tests/test_drain.py tests/test_reconcile.py tests/test_daemon_soak_runner.py
uv run pytest -q tests/test_daemon_composition.py tests/test_daemon_tasks.py tests/test_kill_signal_journal.py tests/test_storm_hold.py tests/test_bug_gate.py tests/test_rework.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A missing or contradictory owning entry fact returns premise_failed with kind: spec_gap and its unit. A criteria-forced path beyond the recorded closure returns premise_failed for plan repair.

## Time budget
- expected: 60m
- stuck: 90m
