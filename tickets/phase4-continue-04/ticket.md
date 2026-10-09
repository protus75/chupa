---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- reliability-battery

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P4
- section 13
- 19.P4.reliability-run
- 19.P4.reliability-battery

## Goal / Why
Check can review and lift the no-code report producer and terminal continuation.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P4 through END_REGISTRY_P4 from committed CHUPA_PLAN.md. Position 04 carries admissions[4:]: [reliability-run], [phase4-exit]. Author only reliability-run and phase4-continue-05. The producer depends on phase4-continue-04, reliability-battery, provider-cooldown-failover and outbox-only-admission; the successor depends on reliability-run and carries admissions[5:]. Keep every registry row and its ordering. Both this admission's seeds start medium/medium; the future terminal phase4-exit starts high/high under 19.L. Cap the batch at seeding.max_seeds_per_admission and stuck budgets at drain.max_ticket_minutes. Do not author phase4-exit in this pass.

Before writing run entry_unit_gap for 19.P4.reliability-run and its required cited 19.P4.reliability-battery. Run resolve_plan_contract for all required entries, registry row citations and seeder-role citations against the merged plan. The terminal lookahead is governed by 19.P4 and 19.L; no uncited later entry is inspected prematurely. Missing or contradictory governing facts return premise_failed, kind: spec_gap, naming the owning cited entry. Cite unit ids; never copy unit text. The producer's citation roles are 19.I, 19.P4.reliability-run and 19.P4.reliability-battery; the successor cites 19.L, 19.I, 19.P4, section 13 and the terminal admission's required next-phase 19.P5. Validate future entry depth in its owning pass.

The next admission realizes the cited no-code producer contract, including every Owner, Records, Observable and Tests obligation. Verification must run uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_merge.py followed by uv run python -m eval.reliability_battery --out tickets/reliability-run/reliability-battery-report.json. The report stays uncommitted; only Check's ordinary registered OUTBOX lift commits it. No code, schema, registration or tests are authored by the producer. Pin fresh all-green member-local evidence, source provenance, purge/current-report requirement, checks-only custody, inherited-copy exclusion, empty code diff, exact producing-lift custody, null-commit settlement and one retirement. Failed output, Verification or lift cannot settle. The producer command must run at Verification even when Implement sees existing output; already_satisfied is no substitute. Inject time and fixture providers; no live calls, config edits or wall waits.

Named producer proofs: test_reliability_battery_command_writes_only_on_green, test_reliability_battery_requires_member_local_evidence, test_reliability_battery_uses_registered_checks_lift, test_outbox_only_check_accepts_registered_report, test_outbox_only_check_requires_current_report, test_outbox_only_merge_regate_requires_lift_custody, test_outbox_only_admission_records_null_commit_and_retires. Run merged preservation suites unchanged; do not fence or embed them.

Read owners, predecessor tickets, direct callers and named tests. Grep signatures, composition sites, allowlists and contradicted/absence assertions across chupa/, eval/ and tests/. Earn additions only under 19.L rules 2-5 or cited seam-owner closure; pin each path's precise reason. Existing fenced paths default to Context. Only measured breach of the 300,000-character headroom earns On-demand. Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files never enter Context. Historical seeding snapshots remain immutable.

Use merged tests/test_seeded_phase3_core.py as the idiom and create tests/test_seeded_phase4_04.py with test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_dependencies_as_authored, test_stuck_budget_fits_the_drain_envelope, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots. Pin exact identity, confirmed birth, intake grammar, edges, citation roles, required entry depth, every named obligation, earned closure and Context/On-demand partition. Record authoring head, merged idiom blob, file and ticket sizes and cited-unit lengths. Use fixed authoring snapshots for max-effort renders; never live sizes or live plan lengths.

Write only the two new seeds directly, leaving them uncommitted; commit only the new batch test. Check owns requisition_review, tickets/phase4-continue-04/checks.json approvals and one ticket-plane seed lift. Keep approved bytes while ticket_sha matches and re-author only snagged seeds. Out: implementation, existing tickets/run records, Box messages, manual release, later admissions and plan edits.

## Scope fence
- tickets
- tests/test_seeded_phase4_04.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase4_04.py` exits 0 proving exactly the producer and successor with grammar, edges, citation roles, depth, obligations, closure and fixed renders.
2. `tickets/phase4-continue-04/checks.json` records approvals before Check performs one ticket-plane seed lift; the code commit contains only the batch test.
3. `uv run pytest -q` exits 0 preserving historical snapshots and merged behavior.

## Verification
```
uv run pytest -q tests/test_seeded_phase4_04.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap, naming the owning cited unit. A criteria-forced path outside the earned fence requires contract repair; never invent facts or change the registry.

## Time budget
- expected: 60m
- stuck: 90m
