---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase5-continue
- retro-drain-invoker

## Context
- chupa/policy.py
- chupa/status.py
- tests/test_policy.py
- tests/test_box.py
- tests/test_vocabularies.py
- tests/test_author.py
- chupa/author.py
- tests/test_triage.py
- chupa/box.py
- chupa/triage.py
- chupa/journal.py
- chupa/retro.py
- tests/test_retro.py
- chupa/__main__.py
- chupa/merge.py
- chupa/serve.py
- chupa/driver.py
- chupa/daemon.py
- tests/test_merge.py

## On-demand
- chupa/stages.py
- chupa/runner.py
- chupa/drain.py
- tests/test_stages.py
- tests/test_daemon_composition.py
- tests/test_drain.py
- tests/test_serve.py

## Plan contract
- 19.I
- 19.P5.retro-box-activation
- section 12

## Goal / Why
Completed retro proposals reach the existing Box, triage, Author and successful prompt-spec admission with durable provenance; tombstone re-reports reopen observably.

## Scope in / Scope out
This registry row is KNOWN-DEEP: production proposal evidence crosses retro, queue, triage, authoring, policy and admission seams, earning high/high birth. Read every Context and On-demand path before editing. Follow the cited entry's Owner, Records, Observable and Tests; introduce no new module. chupa/retro.py emits completed-report proposals and reads tombstones; chupa/box.py owns queue writes and both dedup layers' shared re-report counter; chupa/triage.py retains the sequential consumer and chupa/author.py the sole ticket author. chupa/policy.py keeps start_state and chupa/merge.py owns successful merge evidence.

Use the completed retro/<seq> effect identity, canonical sorted compact UTF-8 proposal JSON, ordered proposed_spec_paths, and the first 16 lowercase SHA256 hex characters for proposal identity. Store the exact proposal evidence and stable arrival identity through the Box/storm seam. Completion precedes emission; incomplete reports cannot emit and replay cannot duplicate messages. Retain existing closed Message, Verdict, Resolution and DecisionRecord contracts while adding only the entry's class-specific fields and reports/reopen queue fields.

Signature and semantic dedup both invoke Box.record_rereport on the tombstoned target. Prove original arrival versus re-report, below/at K=3, post-increment count, restart/replay identity, and one threshold crossing. The journal-backed callback appends tombstone_auto_reopened at tombstone-reopen/<box_id>/<reports> with kind, box_id, signature and reports before clearing resolution. Missing callback raises RereportCallbackRequired with a supply-callback road while preserving the increment and tombstone; failed append preserves resolution. Reopen clears stale verdict and resolution, returns pending, marks reopen true, and preserves committed registry bytes. Both fresh semantic dedup and existing-record recovery bypass the reopened target's old tombstone.

After the existing ticket-plane commit, Author writes retro_ticket_authored at retro-ticket/<stem> with kind, box_id, retro_report_key and ticket_stem, then resolves the Box item. Keep source box:retro_finding and refuse conflicting replay provenance. Before main mutation, merge requires one unique matching Author bridge. Missing or conflicting bridges refuse with a restoration road. A successful admission changing prompt specs writes retro_prompt_spec_change_merged at retro-prompt-spec-change/<stem>/<squash-sha> with kind, box_id, retro_report_key, ticket_stem, squash_sha and changed_spec_paths. Derive the sorted actual specs/*.md paths and real squash SHA from successful admission; failed, unrelated and no-spec admissions emit nothing; replay emits once.

Propagate the message reopen marker into policy.start_state(reopen=...) at candidate review. Under binding GO every reopened ticket still starts draft; retain absent/drifted GO, safety-inventory and bypass overrides, grammar/requisition review and Effects custody. Class-based visibility uses message_class and its policy row, never message priority. Status surfaces confirmed-class tombstones and retro itemizes them with reopen signals without queue writes.

Bind the journal-backed callback in every journal-holding production Box: direct operator triage, bootstrap ingestion, the shared storm_producer wrapper and its driver, stages, runner, daemon, drain, serve, CLI and retro compositions. Preserve storm_producer's public signature so existing callers inherit the binding. Reuse the production composition harness in tests/test_daemon_composition.py; removing any production binding must fail the new constructor test. Bootstrap drain still never scans the Box; daemon scheduling stays sequential and its worker/task counts stay fixed. Preserve the public Stages.driver/Pipeline.stages access; add no Driver access, author, consumer or writer lane.

Earned fence additions: chupa/journal.py and tests/test_vocabularies.py cover the three new closed signal names; tests/test_status.py owns the entry's status visibility obligation; tests/test_retro.py owns tombstone itemization and the predecessor empty-Box assertion invalidated by completed proposal emission; chupa/driver.py covers its journal-backed shared producer caller. Migrate only the last empty-Box assertion in test_receipt_uses_engine_provenance_usage_calibration_and_tombstones to evidenced proposal emission, preserving its report JSON, commit, usage and calibration checks. Keep all non-firing predecessor and scheduling assertions unless this activation actually invalidates one.

Create tests/test_retro_box.py for the composed completion-to-prompt-spec-merge proof and test_retro_box_entry_unit: required_units must require 19.P5.retro-box-activation for both the row and its owning continuation; resolve_plan_contract with duplicate citations must resolve it exactly once; entry_unit_gap must return None. Keep tests/test_plan_lint.py green unchanged; its run belongs only in Verification. Named creation/retention obligations:
- test_completed_retro_proposals_reach_prompt_spec_merge
- test_tombstone_rereports_reopen_at_threshold
- test_tombstone_reopen_requires_journal_callback
- test_reopened_message_bypasses_its_tombstone
- test_reopened_retro_ticket_starts_draft
- test_standing_go_uses_the_table_and_each_override_drafts
- test_retro_prompt_spec_merge_requires_unique_bridge
- test_production_boxes_receive_rereport_callback
- test_retro_itemizes_confirmed_class_tombstones
- test_status_surfaces_confirmed_class_tombstones
- test_tombstone_visibility_uses_message_class

Each named obligation proves the cited entry's complete invariant, including exact signal bodies/keys, successful path/SHA evidence, both dedup layers, class visibility, write-free reads, reopen override and every production constructor. Use disposable repos and injected clock, filesystem, process and scripted model seams. Leave baseline-binding-reader, scorecard reporting, supervised admission, later verbs and new scheduling to their owning rows. Do not edit prompt specs or historical seeding tests.

## Scope fence
- chupa/retro.py
- chupa/box.py
- chupa/merge.py
- chupa/author.py
- chupa/triage.py
- chupa/policy.py
- chupa/stages.py
- chupa/runner.py
- chupa/daemon.py
- chupa/drain.py
- chupa/serve.py
- chupa/status.py
- chupa/__main__.py
- tests/test_box.py
- tests/test_merge.py
- tests/test_author.py
- tests/test_triage.py
- tests/test_policy.py
- tests/test_stages.py
- tests/test_daemon_composition.py
- tests/test_drain.py
- tests/test_serve.py
- tests/test_retro_box.py
- chupa/journal.py
- tests/test_vocabularies.py
- tests/test_status.py
- tests/test_retro.py
- chupa/driver.py

## Acceptance criteria
1. `uv run pytest -q tests/test_retro_box.py` exits 0 proving the real completed report -> Box -> triage -> Author -> prompt-spec merge chain, canonical identity, exact evidence, replay/incomplete refusal, successful squash SHA/path evidence and required_units/resolve_plan_contract/entry_unit_gap depth.
2. `uv run pytest -q tests/test_box.py tests/test_triage.py tests/test_author.py tests/test_policy.py tests/test_merge.py` exits 0 proving both re-report layers, callback custody, recovery without re-tombstoning, unconditional reopen draft and unique pre-mutation bridge validation.
3. `uv run pytest -q tests/test_daemon_composition.py tests/test_status.py tests/test_retro.py tests/test_vocabularies.py` exits 0 proving every production callback, class-based tombstone visibility/itemization, closed vocabulary and preserved predecessor evidence.
4. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged behavior, existing scheduling and non-firing assertions.

## Verification
```
uv run pytest -q tests/test_retro_box.py
uv run pytest -q tests/test_box.py tests/test_triage.py tests/test_author.py tests/test_policy.py tests/test_merge.py
uv run pytest -q tests/test_daemon_composition.py tests/test_status.py tests/test_retro.py tests/test_vocabularies.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q tests/test_drain_upgrade.py tests/test_seed_successor.py tests/test_cli.py tests/test_daemon_config.py tests/test_daemon_admission.py tests/test_daemon_pause.py tests/test_reconcile.py tests/test_flake.py tests/test_storm_hold.py tests/test_storm_notification_activation.py tests/test_drain_reentry.py tests/test_ladder.py tests/test_diagnose.py tests/test_harvest.py tests/test_audit.py tests/test_storm_producer.py tests/test_provider_cooldown_failover.py tests/test_watchdog_activation.py tests/test_restart_timers.py tests/test_kill_cli_activation.py tests/test_kill_executor_abort.py tests/test_kill_signal_journal.py tests/test_seed_path.py tests/test_reject_queue.py tests/test_caps.py tests/test_control_cli.py tests/test_daemon_tasks.py tests/test_heartbeat.py tests/test_checkpoint.py tests/test_kill_worker_stop.py tests/test_kill_failure_suppression.py tests/test_driver.py tests/test_storm.py tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap, unit: 19.P5.retro-box-activation. A criteria-forced file outside this fence requires ticket repair. No second problem belongs in this diff.

## Time budget
- expected: 90m
- stuck: 180m
