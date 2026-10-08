---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-24

## Context
- chupa/artifacts.py
- chupa/stages.py
- chupa/git.py
- chupa/seams.py
- chupa/effects.py
- eval/shakeout/run.py

## Plan contract
- 19.I
- 19.P3.daemon-soak

## Goal / Why
Make the closed daemon soak report validate and use the existing checks report lane.

## Scope in / Scope out
Implement only the daemon-soak registry row. The renderer supplies Owner, Records, Observable and Tests from 19.P3.daemon-soak; cite them rather than copying unit text. That entry governs schema, provenance, strict ordered membership, false-green refusal, the filesystem writer, registration and no machinery-produced exit report. The new eval/daemon_soak.py is the canonical writer's owner under that entry. It adds neither a runner nor a producing run; the later runner and separate soak-run earn exit evidence.

Pin the entry's obligations in test_daemon_soak_schema_is_closed, test_daemon_soak_green_matches_observation_and_auditor, test_daemon_soak_writer_validates_before_write and test_daemon_soak_uses_registered_checks_lift, through 19.P3.daemon-soak. Cover validation before any filesystem write, canonical bytes, invalid/red refusal without mutation and real registration using the merged checks lift. Synthetic construction values never become an exit artifact.

Preserve report-purge before Verification, schema-validation, named-report-required behavior, checks-only custody and inherited byte-equal exclusion. Run tests/test_stages.py as an unchanged preservation suite: test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass and test_outbox_only_check_requires_current_report pin these predecessor obligations. The checks lift alone commits registered reports. No additional lift lane, event, signal, frontmatter or configuration field is earned.

Read merged artifacts and stages, the eval/shakeout/run.py report writer precedent, Git/Effects, runner, daemon, CLI run/drain and build_daemon_core, serve composition, Journal, Restart, Timers and the merged production-composition harness before changing their owned boundary. Journal alone writes durable events, Box alone writes queue records and ControlInbox alone writes control decisions. Preserve Journal(state_dir, clock), append/read/close signatures, bootstrap on-entry reconciliation and ordinary DaemonTasks exception propagation and cleanup. The writer uses the supplied filesystem seam; it performs no Git or journal mutation. Provenance follows the governing entry and real Git.rev_parse evidence.

The authoring closure grep across chupa/, eval/ and tests/ found no earned fence additions: the registry floor covers the models, registration and new writer/test. Dynamic report discovery, purge, validation and checks lift already consume KNOWN_ARTIFACTS; existing call signatures and composition wiring stay intact. No allowlist or production absence assertion changes. Existing fenced paths are Context; created paths belong in neither Context nor On-demand. The embedded render fits the 300,000-character headroom.

Where production exercise applies, use injected seams, scripted callbacks, disposable synthetic repositories and asyncio barriers through the real CLI/async serve entrypoint and merged production-composition harness. No test-only graph, live host work, real-model calls, wall-clock waits, notify transport or routing changes. Out: runner implementation, report production or publication, tickets/run records, historical seeding snapshots and unrelated fixes.

## Scope fence
- eval/daemon_soak.py
- chupa/artifacts.py
- chupa/stages.py
- tests/test_daemon_soak.py

## Acceptance criteria
1. `uv run pytest tests/test_daemon_soak.py tests/test_stages.py` exits 0 with all four named entry obligations proving the report schema, false-green refusal and canonical writer.
2. `uv run pytest tests/test_daemon_soak.py tests/test_stages.py` exits 0 proving real registration and the existing checks lift, including invalid-byte refusal and checks-only custody without a machinery-produced exit report.
3. `uv run pytest tests/test_daemon_soak.py tests/test_stages.py` exits 0 with the unchanged preservation suite proving purge, validation, named output and inherited-copy exclusion.

## Verification
```
uv run pytest tests/test_daemon_soak.py tests/test_stages.py
```

## Definition of rejected
A required fact missing or contradictory in 19.P3.daemon-soak returns premise_failed, kind: spec_gap, naming that unit; a forced path outside this earned fence also returns premise_failed. Never invent the contract or widen the fence.

## Time budget
- expected: 60m
- stuck: 90m
