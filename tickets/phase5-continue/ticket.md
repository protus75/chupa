---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- retro-drain-invoker

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P5
- 19.P5.retro-box-activation
- section 12
- section 13

## Goal / Why
Check admits the next Phase 5 deep activation and its one shrinking continuation.

## Scope in / Scope out
Parse BEGIN_REGISTRY_P5 through END_REGISTRY_P5 from committed CHUPA_PLAN.md; keep every row and admission in order. Position 01 carries admissions[1:]; author only retro-box-activation plus phase5-continue-02. The exact shrinking suffix is:
- retro-box-activation
- scorecard-reporting
- status-projection, baseline-binding-reader
- retro-doctor-cli
- phase5-exit

The activation depends on this continuation and on retro-drain-invoker, retaining the registry consumption edge; phase5-continue-02 depends only on retro-box-activation. No forward dependency is permitted. Preserve the next row's KNOWN-DEEP high/high birth; the successor seeder starts medium/medium, owns only tickets and its new numbered seeding test, and carries position 02 with admissions[2:]. Each next seeder depends on every payload of the admission before it. The terminal admission emits only phase5-exit and no successor. Do not author any other payload here or seed beyond this phase.

Before writing either seed, run resolve_plan_contract for governing, row and seeder-role ids, and entry_unit_gap for every non-exit unit returned by required_units. Validate both the activation entry and the future successor's required entry in this owning pass. Return premise_failed, kind: spec_gap, with the owning cited unit on missing or contradictory facts. Cite unit ids in Plan contract; never copy their text. The activation cites 19.I, 19.P5.retro-box-activation and section 12. The successor cites the seeder role's 19.L, 19.I, 19.P5, next admission entry and row ids; no whole section 19. Read each entry's Owner, Records, Observable and Tests. Keep all named obligations, including every production constructor, the exact bridge signals, successful spec-change path/SHA evidence, class-based tombstone visibility, reopen override and both dedup layers. Leave the later baseline reader and scorecard to their rows.

Named activation obligations: test_completed_retro_proposals_reach_prompt_spec_merge, test_tombstone_rereports_reopen_at_threshold, test_tombstone_reopen_requires_journal_callback, test_reopened_message_bypasses_its_tombstone, test_reopened_retro_ticket_starts_draft, test_standing_go_uses_the_table_and_each_override_drafts, test_retro_prompt_spec_merge_requires_unique_bridge, test_production_boxes_receive_rereport_callback, test_retro_itemizes_confirmed_class_tombstones, test_status_surfaces_confirmed_class_tombstones, test_tombstone_visibility_uses_message_class. Include test_plan_lint plus required_units, resolve_plan_contract and entry_unit_gap. A newly named test is a creation obligation, never existing Context. New module ownership comes only from the owning entry. Apply caller/activation/closed-vocabulary closure from 19.L rules 2-5 after reading owners/predecessors and grepping signatures, compositions, allowlists and negatives across chupa/, eval/ and tests/. Add chupa/journal.py and tests/test_vocabularies.py for tombstone_auto_reopened, retro_ticket_authored and retro_prompt_spec_change_merged; add tests/test_status.py for the entry's named status visibility obligation. Pin each further earned addition with a precise reason. Every journal-holding production Box constructor, operator triage, bootstrap ingestion and shared storm_producer caller must receive the journal-backed rereport callback. Preserve every scheduling and non-firing predecessor assertion unless this activation actually flips it. Do not invent another author, consumer, writer lane or public Driver access.

Create the fenced batch test using merged tests/test_seeded_phase3_core.py as the earlier idiom. Pin the two seeds, confirmed source: seed birth, grammar, exact consumption edges, citation roles, all required entry depths and named obligations, KNOWN-DEEP evidence, finite suffix, cap and budgets. Record authoring head, idiom blob, file/ticket byte and character sizes, entry hashes and cited-unit lengths. Existing fenced paths default to Context; On-demand is earned only by measured overflow of 300,000-character maximum-effort headroom. Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files never enter Context. Compute render bounds solely from fixed authoring snapshots; never live sizes or plan lengths. Historical seeding snapshots remain immutable. Unchanged preservation suites belong only in Verification, neither fence nor Context.

Write the two new seeds directly and leave them uncommitted; commit only the new batch test. Check owns requisition_review, tickets/phase5-continue/checks.json approvals and a single ticket-plane seed lift. Retain approved bytes while ticket_sha matches; re-author only snagged seeds. Cap the batch at seeding.max_seeds_per_admission and both stuck budgets at drain.max_ticket_minutes. Out: production implementation, existing ticket/run-record edits, plan edits, Box messages, later admissions and manual release.

## Scope fence
- tickets
- tests/test_seeded_phase5_01.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase5_01.py` exits 0 proving exactly retro-box-activation and phase5-continue-02, confirmed birth, grammar, dependency/citation roles, required entry depths, every named obligation, earned closure and fixed maximum-effort renders.
2. `tickets/phase5-continue/checks.json` records requisition_review approvals before one Check ticket-plane lift; only the new batch test belongs to the code commit.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged behavior and historical authoring snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase5_01.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A missing governing fact is premise_failed, kind: spec_gap, naming its owning cited unit. A criteria-forced path outside the earned fence requires contract repair; never widen speculatively or fabricate evidence.

## Time budget
- expected: 60m
- stuck: 180m
