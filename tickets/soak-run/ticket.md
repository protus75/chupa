---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-26

## Context
- chupa/artifacts.py
- chupa/stages.py
- chupa/merge.py
- chupa/git.py
- chupa/effects.py
- chupa/seams.py
- chupa/serve.py
- chupa/daemon.py
- chupa/journal.py
- chupa/box.py
- chupa/control.py
- chupa/reconcile.py
- chupa/audit.py
- chupa/restart.py
- chupa/timers.py

## Plan contract
- 19.I
- 19.P3.soak-run

## Goal / Why
Generate fresh production soak evidence for the ordinary checks lift and Phase 3 exit.

## Scope in / Scope out
Invoke the already merged runner and canonical writer as governed by 19.P3.soak-run. Its injected Owner, Records, Observable and Tests govern the sole report deliverable, source-HEAD provenance, current-run evidence and existing lane custody. This producer owns no code or test module. The dependency reaches daemon-soak-runner, daemon-soak and outbox-only-admission through the seeding chain.

Read eval/daemon_soak.py from disk before invoking its public produce and write_report surfaces: its delimiter-bearing source cannot be Context. Read the forced predecessor tickets and direct callers across chupa/, eval/ and tests/, including tests/test_daemon_soak.py and tests/test_daemon_soak_runner.py, as read-only references. The four suites in Verification are unchanged preservation suites, neither fenced nor embedded. No existing signature, public allowlist, composition binding or absence assertion changes; no addition to the registry report-path floor is earned under 19.L rules 2-5.

The entry supplies the three primary obligations; carry the merged schema, writer, registration and custody obligations unchanged:
test_daemon_soak_command_writes_report_only_on_green, test_daemon_soak_requires_member_local_evidence, test_daemon_soak_is_rederivable, test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write, test_daemon_soak_uses_registered_checks_lift, test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report, test_outbox_only_check_accepts_registered_report, test_outbox_only_admission_records_null_commit_and_retires.

Preserve report-purge before Verification, schema-validation, named-report-required behavior, checks-only custody and inherited byte-equal exclusion. Run both preservation commands before the production report command. No test-authored fixture report substitutes for production evidence. An Implement-only report, inherited copy or already_satisfied claim does not discharge fresh Check production.

Leave the report uncommitted for the checks lift; never hand-copy, patch or Git-add it. chupa/stages.py alone lifts registered reports through ticket-plane/soak-run/<attempt>/checks. chupa/merge.py retains the existing empty-code-diff run-lane admission, null commit, reviewed SHA and single retirement. Journal alone writes durable events, Box alone writes queue records and ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup.

Out: code changes, new tests, schema or registration edits, new records or signals, manual admission, live-host work, wall-clock soak, report commits and unrelated fixes.

## Scope fence
- tickets/soak-run/daemon-soak-report.json

## Acceptance criteria
1. `uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py` exits 0, including the three entry obligations and preserved schema/writer/lift proofs.
2. `uv run pytest tests/test_stages.py tests/test_merge.py` exits 0 preserving purge, validation, named output, current checks custody, inherited exclusion and null-commit retirement.
3. `uv run python -m eval.daemon_soak --out tickets/soak-run/daemon-soak-report.json` exits 0 and leaves the schema-valid current-run report uncommitted, with all ordered members green and actual source-HEAD provenance.
4. `tickets/soak-run/daemon-soak-report.json` reaches main only through the registered checks lift; the existing run-lane admission settles the empty code diff once.

## Verification
```
uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py
uv run pytest tests/test_stages.py tests/test_merge.py
uv run python -m eval.daemon_soak --out tickets/soak-run/daemon-soak-report.json
```

## Definition of rejected
A needed fact missing or contradictory in 19.P3.soak-run returns premise_failed, kind: spec_gap, naming that unit for section 11.4 hardening. A failed command or forced path outside the report-only fence returns premise_failed; never invent evidence or widen the fence.

## Time budget
- expected: 30m
- stuck: 60m
