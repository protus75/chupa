---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase4-continue-03

## Context
- chupa/artifacts.py
- chupa/stages.py
- chupa/providers.py
- chupa/timers.py
- chupa/audit.py
- chupa/journal.py
- chupa/seams.py
- chupa/git.py
- chupa/runner.py
- chupa/driver.py
- tickets/provider-cooldown-failover/ticket.md

## Plan contract
- 19.I
- 19.P4.reliability-battery
- 19.P4.provider-cooldown-failover
- section 6

## Goal / Why
Closed reliability battery machinery is available to the separate producer.

## Scope in / Scope out
Build all machinery governed by the cited battery entry's Owner, Records, Observable and Tests. eval/reliability_battery.py owns produce and write_report; chupa/artifacts.py owns ReliabilityBatteryEntry, ReliabilityBatteryReport and their constants; chupa/stages.py owns registration. Construction returns a report but publishes no exit artifact at import or engine startup. reliability-run is the separate later producer. Implement every entry obligation through its citation, without duplicating the entry's prose.

Exercise the merged production composition with a multi-candidate fixture registry and scripted CLI failures. Read chupa/daemon.py, chupa/drain.py, chupa/serve.py, chupa/__main__.py and the production-composition harness on disk before wiring the fixture; use no tests imports or invented successful evidence. Keep one provider payload and one Timers lifetime, existing Driver/dispatcher/runner harvest, and the journal and auditor owners. No routing or cooldown algorithm is reimplemented. Re-grep signatures, constructors, public allowlists and absence assertions across chupa/, eval/ and tests/; the existing signatures remain intact and there are no earned fence additions.

The three members are classified_quota_exhaustion, all_candidates_cooling_recovery and unclassified_failure_preservation. Require the quota member's real classification, harvested failed terminal, exact persisted cooldown deadline and absence of infra draw or inline retry. Exhaust the fixture candidates in order, read the cost-free drought hold with no call, cap, diagnosis or Reject arrival, advance injected time to the earliest deadline, read matching timer_fired, then read automatic recovery and matching result/completion/run-record served identity. The unknown failure remains unclassified with normal infra accounting and captured error evidence; never manufacture a successful call or quota class.

Use member-local production records and the entire member journal; producing_run identifies that member's fault-producing attempt. audit_journal supplies ordered violation descriptions. Missing evidence, contradictory evidence, cross-member evidence or a supplied success/auditor verdict must refuse green. Stop and await owned lifetimes before auditing; Git cleans disposable worktrees on success, failure and cancellation. Inject clock, sleep, process-exec and filesystem seams; use no live provider, config change or wall-clock wait.

Prove closed schema fields and strict types, fixed expected values, unique complete member order, run identity, inherited version policy and spec/source-HEAD provenance. Prove observation-plus-auditor green equality and false-green rejection. The canonical writer revalidates, refuses red/invalid reports without writing, and writes canonical UTF-8 JSON with its trailing newline through FileSystem.write, with no Git or journal action. Register the report under its own name in KNOWN_ARTIFACTS. Preserve purge before Verification, schema validation, named-report-required, checks-only custody and inherited-copy exclusion. The real command uv run python -m eval.reliability_battery --out <path> calls the writer only for all-green completion and refuses with a member-specific repair road otherwise; it adds no selector, committer or automatic invocation.

Named obligations: test_reliability_battery_schema_is_closed, test_reliability_battery_green_requires_observation_and_auditor, test_reliability_battery_writer_validates_before_write, test_reliability_battery_uses_registered_checks_lift, test_classified_quota_exhaustion, test_all_candidates_cooling_recovery, test_unclassified_failure_preservation, test_reliability_battery_requires_member_local_evidence, test_reliability_battery_cleans_up_owned_lifetimes, test_reliability_battery_command_writes_only_on_green. Each named test covers every case assigned to it by the entry citation. Preserve custody obligations test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report. tests/test_stages.py, tests/test_provider_cooldown_failover.py and tests/test_audit.py are unchanged preservation suites, present only in Verification. Created paths enter neither Context nor On-demand. All existing fenced paths are embedded in Context.

Out: production signature changes, new records/signals/frontmatter/config/gates/lift paths, report production for the exit, report commits, later admissions, plan changes and historical seeding test edits.

## Scope fence
- eval/reliability_battery.py
- chupa/artifacts.py
- chupa/stages.py
- tests/test_reliability_battery.py

## Acceptance criteria
1. `uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_provider_cooldown_failover.py tests/test_audit.py` exits 0 proving every entry-named schema, writer, production member, evidence, cleanup and command obligation.
2. `uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_provider_cooldown_failover.py tests/test_audit.py` exits 0 preserving report registration and custody, with no machinery-produced exit artifact.

## Verification
```
uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_provider_cooldown_failover.py tests/test_audit.py
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap, naming the owning cited unit. A criteria-forced path outside the earned fence requires contract repair; never invent facts or change the registry.

## Time budget
- expected: 60m
- stuck: 90m
