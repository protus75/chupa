---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-23

## Context
- chupa/stages.py
- chupa/merge.py
- tests/test_stages.py
- tests/test_merge.py

## Plan contract
- 19.I
- 19.P3.outbox-only-admission
- 19.L
- section 10

## Goal / Why
Admit a reviewed no-code producer only when its current checks lift has committed a registered, valid report.

## Scope in / Scope out
Implement the cited 19.P3.outbox-only-admission entry in its existing owners. The renderer supplies Owner, Records, Observable and Tests; cite them rather than duplicating plan prose here. This deep registry row earns the high/high start.

Named obligations governed by 19.P3.outbox-only-admission: test_outbox_only_check_accepts_registered_report, test_outbox_only_check_requires_current_report, test_outbox_only_check_failure_never_admits, test_outbox_only_admission_records_null_commit_and_retires, test_outbox_only_merge_regate_requires_lift_custody, test_outbox_only_exception_preserves_code_lane_safety. Keep these predecessor obligations green: test_empty_diff_claimed_ok_fails_verification, test_already_satisfied_is_proven_by_green_verification_and_skips_review, test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass. Pin current-run output and purge before Verification, schema validation, checks-custody, matching lift custody at regate, null-commit settlement, unchanged code tree, retirement, replay, approval and code-lane safety to that entry's tests. Include rejected evidence cases and ordinary code/report coexistence as that unit requires.

Record custody stays with the cited owners: stages.py discovers and validates reports, and its existing checks lift alone commits them; merge.py owns Admission.commit and the shared admission writer and terminal. MergeQueue calls write_squash without a signature change, retaining checked-tree, integration and hold behavior. Journal alone writes durable events, Box alone writes queue records, and ControlInbox alone writes control decisions. Keep Journal(state_dir, clock), append/read/close, bootstrap on-entry reconciliation, Restart/Timers ownership, and ordinary DaemonTasks exception propagation and cleanup. MERGE_SPEC_VERSION remains governed by the entry.

Authoring closure found no earned fence additions. Keep the four registry floor paths embedded as Context. Ordinary empty-ok still fails: preserve the existing empty-diff message used by eval/shakeout/stages.py, updating its paved road within stages.py. No ordinary-code Admission.commit assertion or production absence assertion is invalidated by the report exception. Public signatures, composition wiring and caller arity stay intact; no further fence widening is presumed. Read the merged queue, runner, daemon, CLI run/drain/build_daemon_core, serve, Journal, Restart, Timers and production-composition harness on demand as read-only references before changes that depend on them.

Production evidence must exercise real stages and real checks lifting via Git/Effects, including inline and serve-selected admission. Reuse the merged production-composition harness where applicable through the real CLI/async serve entrypoint, using injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers. Named tests can import existing harness helpers without editing their owners. No live host work, real-model calls, wall-clock waits or test-only composition graph. Audit the producing journals and prove dependency eligibility and checkpoint counting against the unchanged owners.

The six unfenced test files in Verification are unchanged preservation suites: neither fence nor embed them. Preserve report registration custody with its emitting machinery; this ticket adds no schema, report, module, notification transport or routing change. Out: soak machinery, producer work, plan changes, existing tickets, historical seeding snapshots and new admission lanes.

## Scope fence
- chupa/stages.py
- chupa/merge.py
- tests/test_stages.py
- tests/test_merge.py

## Acceptance criteria
1. `uv run pytest tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_cli.py tests/test_drain.py tests/test_audit.py tests/test_checkpoint.py` exits 0, including the six named 19.P3.outbox-only-admission obligations and the preserved predecessor tests.
2. `uv run pytest tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_cli.py tests/test_drain.py tests/test_audit.py tests/test_checkpoint.py` exits 0 proving current checks custody, initial Check and both shared-writer admission modes against the cited entry.
3. `uv run pytest tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_cli.py tests/test_drain.py tests/test_audit.py tests/test_checkpoint.py` exits 0 proving null-commit provenance, one retirement, replay, unchanged code tree, approval and code-lane safety, with journal audit, dependency eligibility and checkpoint count preservation.

## Verification
```
uv run pytest tests/test_stages.py tests/test_merge.py tests/test_mergequeue.py tests/test_serve.py tests/test_cli.py tests/test_drain.py tests/test_audit.py tests/test_checkpoint.py
```

## Definition of rejected
A needed governing entry missing a fact or contradicting merged behavior returns premise_failed, kind: spec_gap, naming that unit for section 11.4 hardening. A forced file beyond an earned fence returns premise_failed; do not invent a contract or widen scope while implementing.

## Time budget
- expected: 60m
- stuck: 90m
