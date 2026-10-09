---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase4-continue-05

## Context
- chupa/artifacts.py
- chupa/git.py
- chupa/seams.py
- chupa/effects.py
- chupa/runner.py
- chupa/drain.py
- chupa/__main__.py
- tests/test_seeded_phase3_core.py
- tickets/reliability-run/reliability-battery-report.json
- tickets/watchdog-activation/checks.json

## Plan contract
- 19.L
- 19.I
- 19.P4
- section 13
- 19.P5
- 19.P5.retro-drain-invoker
- section 14
- 19.P5.retro-box-activation
- section 12

## Goal / Why
Read the committed Phase 4 exit evidence and admit only the Phase 5 core and its first continuation.

## Scope in / Scope out
This sole terminal Phase 4 payload starts high/high: 19.L names phase exits KNOWN-HARD. Its predecessor phase4-continue-05 transitively covers watchdog-event-stream, notify-transport, watchdog-detector, watchdog-activation, provider-cooldown-failover, reliability-battery and reliability-run. Create tests/test_phase4_exit.py with test_phase4_exit_dependency_coverage asserting that exact registry coverage by traversing committed predecessor tickets. Dispatch supplies the merged-presence proof. Use the existing Git seam to read code-deliverable squash trailers (chupa-ticket) at most; do not invent Git methods or cross-check approval provenance. reliability-run is the no-code producer with a null code commit, so no code squash trailer is demanded for it. Accept a rejected predecessor only with its merged same-goal successor and corresponding rewired coverage under 19.L.

In test_phase4_exit_reads_committed_reliability_report, read tickets/reliability-run/reliability-battery-report.json through ReliabilityBatteryReport and RELIABILITY_BATTERY_REPORT. Require classified_quota_exhaustion, all_candidates_cooling_recovery and unclassified_failure_preservation in that closed order, each green with observed equal to expected and an empty member-local auditor; require producing_run and source/spec provenance. Machinery emitter reliability-battery owns the schema in chupa/artifacts.py, registration in chupa/stages.py, and eval/reliability_battery.py's canonical writer and production runner. Later emitter reliability-run produces the report after machinery merges. Keep the multi-candidate fixture registry, production observations and full member-local auditor evidence. The exit only consumes that committed report; it never calls its producer or writer, refreshes it, copies it into git, or writes fixture exit evidence. No separate Phase 4 report is specified. Preserve engine-lane custody, checks-only registered report lifting and the producer/machinery separation.

In test_phase4_exit_reads_committed_soft_band_check and test_phase4_exit_reads_committed_hard_timeout_check, read watchdog-activation's committed tickets/watchdog-activation/checks.json through Invoice in chupa/stages.py. Require passed, an unbypassed passing verification report and rc=0 for the recorded Verification command running tests/test_watchdog_activation.py. Read the merged named tests, then run tests/test_watchdog_activation.py::test_production_soft_band_notifies_once_without_kill and tests/test_watchdog_activation.py::test_production_hard_timeout_group_kill_is_harvested unchanged at Check. Emitters watchdog-detector/watchdog-activation own these wired production-composition proofs: the first observes one spiral-warning notify intent/completion pair per run without auto-kill; the second observes hard-timeout process-group kill, reap and committed harvested output. A suite-level checks receipt plus these named merged proofs is the read surface; never claim that checks.json stores per-test results. Do not read live journal or depend on a conditional event in the healthy drain. An unmet artifact, member, dependency or production proof returns premise_failed naming the read.

Parse BEGIN_REGISTRY_P5 through END_REGISTRY_P5 from committed CHUPA_PLAN.md; preserve every row and admission in order. Author only retro-drain-invoker and phase5-continue, never the second admission's payload here. retro-drain-invoker depends on phase4-exit, starts high/high because its registry row is KNOWN-DEEP, and cites 19.I, 19.P5.retro-drain-invoker, sections 13 and 14. It realizes that entry's invoker and declaration-keyed Exit-read window seam. Name its new module owner chupa/retro.py from the cited entry, with specs/retro.md as the retro prompt source. Leave scorecard, box activation and CLI verbs to later admissions. phase5-continue starts medium/medium, depends on retro-drain-invoker, owns only tickets and its new tests/test_seeded_phase5_01.py, embeds merged tests/test_seeded_phase3_core.py as its earlier idiom, and cites 19.L, 19.I, 19.P5, 19.P5.retro-box-activation, sections 12 and 13. It names position 01 and admissions[1:], authors only retro-box-activation plus phase5-continue-02 when it runs, and carries the shrinking suffix and registry edges without forward dependencies. Preserve that next row's high/high deep start. No later admission is authored by this exit; never inspect or seed beyond Phase 5.

Before writing either seed, run resolve_plan_contract for all governing, row and seeder-role citations and entry_unit_gap for every required non-exit unit identified by required_units, including both 19.P5.retro-drain-invoker and 19.P5.retro-box-activation. Validate the continuation's future entry depth in this pass. Missing or contradictory facts return premise_failed, kind: spec_gap, naming the owning cited unit. Cite unit ids; never copy their text. Read each entry's Owner, Records, Observable and Tests, and preserve all its named test obligations in the authored seed. Read owners and predecessors, including chupa/stages.py and chupa/driver.py from disk, and read the battery runner from disk (its delimiters exclude Context). A newly named entry test that does not yet exist is a creation obligation, never existing Context.

For retro-drain-invoker, grep signatures, composition roots, signal allowlists and absence assertions across chupa/, eval/ and tests/. Apply 19.L rules 2-5 and cited seam-owner closure only; record precise reasons for every addition beyond the registry floor, including chupa/journal.py and its affected allowlist tests. Examine every suite reaching main(["drain"]) through a merge: re-entry, upgrade, kill, storm, restart, provider, watchdog, pause and control. Record either the scenario's forced assertion migration and fence that test, or the non-firing reason and run it unchanged as preservation verification. Do not assume the new forced quiescence/pre-exit call cannot affect existing merged scenarios. No public Driver or Pipeline access may be invented without its owner/caller closure; the entry governs the public read-only Stages.driver through Pipeline.stages.

Create tests/test_seeded_phase5_core.py using the merged Phase 3 idiom. Pin exactly the core and one continuation, confirmed source: seed birth, grammar, consumption edges, citation roles, both required entry depths, deep/high evidence, every named entry obligation, finite suffix, seed cap and budgets. Record authoring head, idiom blob, file/ticket sizes, entry hashes and cited-unit lengths. Pin earned fences with each addition's reason. Existing fenced paths default to Context; On-demand is earned only by measured overflow of 300,000-character headroom. Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files never enter Context. Compute maximum-effort renders solely from fixed authoring snapshots, never live sizes or plan lengths. Keep historical seeding snapshots immutable. Preservation suites run unchanged in Verification, neither fenced nor embedded.

The unchanged preservation proofs include test_reliability_battery_requires_member_local_evidence, test_reliability_battery_green_requires_observation_and_auditor, test_reliability_battery_uses_registered_checks_lift, test_verification_report_lifts_only_in_checks_commit, test_invalid_report_fails_check_without_lifting_checks_or_report, test_implement_report_is_not_lifted_and_stale_report_is_purged, test_named_missing_report_fails_even_when_other_commands_pass, test_outbox_only_check_requires_current_report, test_outbox_only_check_accepts_registered_report, test_outbox_only_merge_regate_requires_lift_custody and test_outbox_only_admission_records_null_commit_and_retires. They retain current-run production evidence and engine-lane custody; run their suites unchanged, neither fenced nor Context.

Cap the two-seed batch at seeding.max_seeds_per_admission and both stuck budgets at drain.max_ticket_minutes. Write both seeds directly and leave them uncommitted. Check owns requisition_review, tickets/phase4-exit/checks.json approvals and one ticket-plane seed lift. Retain approved bytes while ticket_sha matches; re-author only snagged seeds. Commit only the two new tests. Out: production implementation, existing ticket/run-record changes, report refresh, live-state evidence, Box messages, plan edits, later admissions and manual release.

## Scope fence
- tickets
- tests/test_phase4_exit.py
- tests/test_seeded_phase5_core.py

## Acceptance criteria
1. `uv run pytest -q tests/test_phase4_exit.py` exits 0 with test_phase4_exit_dependency_coverage proving every Phase 4 deliverable including reliability-run and watchdog-activation transitively covered, and test_phase4_exit_reads_committed_reliability_report proving all three member-local green observations from the committed report emitted by reliability-battery/reliability-run.
2. `uv run pytest -q tests/test_phase4_exit.py` exits 0 with test_phase4_exit_reads_committed_soft_band_check and test_phase4_exit_reads_committed_hard_timeout_check reading watchdog-activation's passing checks.json for watchdog-detector/watchdog-activation; the two named production tests in Verification prove the notify pair without auto-kill and hard-timeout group kill with harvested output.
3. `uv run pytest -q tests/test_seeded_phase5_core.py` exits 0 proving only retro-drain-invoker and phase5-continue, entry depth and named obligations, confirmed birth, exact edges, high/high core start, citation roles, earned closure and fixed maximum-effort renders under 300,000 characters.
4. `tickets/phase4-exit/checks.json` records requisition_review approvals before Check's single ticket-plane seed lift; only the two new tests belong to the code commit.
5. `uv run pytest -q tests/test_reliability_battery.py tests/test_stages.py tests/test_merge.py` and `uv run pytest -q` exit 0 retaining member-local production evidence, machinery/producer separation, registered checks-only custody and merged watchdog behavior.

## Verification
```
uv run pytest -q tests/test_phase4_exit.py
uv run pytest -q tests/test_seeded_phase5_core.py
uv run pytest -q tests/test_watchdog_activation.py::test_production_soft_band_notifies_once_without_kill tests/test_watchdog_activation.py::test_production_hard_timeout_group_kill_is_harvested
uv run pytest -q tests/test_reliability_battery.py tests/test_stages.py tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
An unmet committed exit read returns premise_failed naming it. Missing governing entry facts return premise_failed, kind: spec_gap, naming their owning cited unit. A criteria-forced path outside earned closure requires contract repair; never widen the registry, invent provenance or fabricate report evidence.

## Time budget
- expected: 60m
- stuck: 90m
