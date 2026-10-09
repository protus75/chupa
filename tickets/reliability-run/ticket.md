---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase4-continue-04
- reliability-battery
- provider-cooldown-failover
- outbox-only-admission

## Context
- chupa/artifacts.py
- chupa/stages.py
- chupa/merge.py
- tickets/reliability-battery/ticket.md
- tickets/provider-cooldown-failover/ticket.md
- tickets/outbox-only-admission/ticket.md

## Plan contract
- 19.I
- 19.P4.reliability-run
- 19.P4.reliability-battery

## Goal / Why
Produce the committed reliability evidence that the Phase 4 exit consumes, through the existing checks lift.

## Scope in / Scope out
Realize every Owner, Records, Observable and Tests obligation in the two cited entry units by running the merged battery. eval/reliability_battery.py owns the runner and canonical writer; chupa/artifacts.py owns ReliabilityBatteryReport and RELIABILITY_BATTERY_REPORT; chupa/stages.py owns checks lifting; chupa/merge.py owns admission and retirement. This producer authors no code, schema, registration or tests. There are no earned fence additions: no public signature, constructor, composition, allowlist or negative assertion changes. Read the owners and predecessor tickets before running. Read eval/reliability_battery.py from disk; its delimiter-bearing source cannot enter Context.

Require fresh all-green member-local evidence for classified_quota_exhaustion, all_candidates_cooling_recovery and unclassified_failure_preservation in that exact order. Each observed value must match its fixed expected value and its entire member-local journal must pass the auditor. producing_run identifies the member's actual fault attempt. Keep spec/source-HEAD provenance, closed report validation and the inherited schema-version policy. Missing, contradictory or cross-member observations and supplied success/auditor verdicts cannot earn green. Use the merged production fixture registry and injected clock, sleep, process-exec and filesystem seams; no live provider calls, config edits or wall waits.

Run both Verification commands in order, even if Implement sees existing output. already_satisfied is no substitute for Verification production. Preserve purge before Verification and the current-report requirement. The canonical writer alone emits complete green output, with canonical UTF-8 JSON and a trailing newline. Leave the report uncommitted: no hand-copy, patch or Git-add. Only the ordinary registered OUTBOX checks lift commits it. Preserve checks-only custody and inherited-copy exclusion; Implement-only output, inherited bytes and test-authored fixture reports cannot supply exit evidence.

Require an empty code diff and no uncommitted code. Read exact producing-lift custody at ticket-plane/reliability-run/<attempt>/checks: its completed result names the report path and ticket-plane commit, and its schema-valid committed main blob matches that lift. Settlement uses the existing to: merged, commit: null and reviewed_sha terminal, with one retirement. Failed output, Verification or lift cannot settle; repair the command's named failed member through the existing failure spine and rerun. Introduce no new records, signals, receipts, configuration, gates or lift paths.

Named proofs: test_reliability_battery_command_writes_only_on_green, test_reliability_battery_requires_member_local_evidence, test_reliability_battery_uses_registered_checks_lift, test_outbox_only_check_accepts_registered_report, test_outbox_only_check_requires_current_report, test_outbox_only_merge_regate_requires_lift_custody, test_outbox_only_admission_records_null_commit_and_retires. Run the merged preservation suites unchanged, neither fenced nor embedded. The destination is created and enters neither Context nor On-demand. Out: implementation, test changes, report commits by Implement, existing tickets/run records, plan edits and later admissions.

## Scope fence
- tickets/reliability-run/reliability-battery-report.json

## Acceptance criteria
1. `uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_merge.py` exits 0 preserving every named producer and custody proof unchanged.
2. `uv run python -m eval.reliability_battery --out tickets/reliability-run/reliability-battery-report.json` exits 0 with a fresh schema-valid, ordered, all-green report carrying member-local evidence and source provenance.
3. `tickets/reliability-run/reliability-battery-report.json` stays uncommitted by Implement; Check's ordinary registered checks lift supplies the exact producing-run custody for empty-code admission, null-commit settlement and one retirement.

## Verification
```
uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_merge.py
uv run python -m eval.reliability_battery --out tickets/reliability-run/reliability-battery-report.json
```

## Definition of rejected
A missing or contradictory governing fact returns premise_failed, kind: spec_gap, naming the owning cited entry. A failed member is repaired through the existing failure spine; never invent evidence, author machinery or widen the fence.

## Time budget
- expected: 60m
- stuck: 90m
