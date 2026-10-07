---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- scheduler-activation

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13
- 19.P3.merge-queue-activation
- 19.P3.rework-activation
- 19.P3.background-consumers
- 19.P3.control-inbox
- 19.P3.dispatch-pause-boundary
- 19.P3.pause-resume-activation
- section 20

## Goal / Why
Advance Phase 3 by exactly one admission: author merge-queue-activation, rework-activation and phase3-continue-07 as confirmed seeds, left uncommitted for Check to review and lift together. This is continuation 06; parse the current plan registry directly. The shrinking unseeded suffix is admissions[6:], its next payload is merge-queue-activation and rework-activation, and its successor starts at admissions[7:]. Never copy the registry into a repository file or alter its rows.

## Scope in / Scope out
Before writing, parse the YAML directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md, never a copied registry. Read the next rows and their complete entry units. Run entry_unit_gap and resolve_plan_contract for 19.P3.merge-queue-activation, 19.P3.rework-activation, 19.P3.background-consumers, 19.P3.control-inbox, 19.P3.dispatch-pause-boundary and 19.P3.pause-resume-activation, and resolve section 20 for the control/pause row citations. Read any further unit a needed citation requires. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening before regeneration; never invent facts.

Author only merge-queue-activation and rework-activation plus phase3-continue-07. Both activation rows start medium/medium because neither is deep. Both depend on phase3-continue-06; the Rework seed explicitly depends on its merge-queue-activation sibling as well as its seeder. Each implementing seed cites exactly 19.I and its own entry unit, since neither row has cite ids. Preserve each row's fence floor. Before widening, grep flipped symbols, old assertion values, public surfaces and direct callers across chupa/, eval/ and tests/. Add only earned 19.L closure rules 2-5 paths and record each path and reason in this batch's new test. Fence every predecessor dormancy/negative assertion and forced composition caller. Existing fenced paths are Context by default; On-demand requires recorded authoring-time measurements proving embedding breaches the 300,000-character headroom. Created paths belong in neither. Prompt-specs and delimiter-bearing sources are never Context. Preservation suites stay unchanged in Verification only, neither fenced nor embedded.

The complete own-entry Owner, Records, Observable and Tests bullets govern each activation payload: carry every owner, exact record shape, sole writer, observable and named invariant test into that payload, together with its full entry-unit Verification command. Extend the same real production root and tests/test_daemon_composition.py harness from scheduler-activation, never a replacement graph. Queue composition belongs in the existing production pipeline binding. Preserve bootstrap run/drain inline admission, accounting, reconciliation, lock lifetime and terminals. Merge-queue activation adds chupa/runner.py under CALLER CLOSURE and migrates test_merge_queue_is_dormant and any graph queue-absence assertion, retaining inline/no-conflict-facts behavior. Its own unit names all six production/transition tests and exact CONFLICT_FACTS, RED_STREAK, TREE_MISMATCH and merge.write_squash record writers; copy those obligations and shapes into the implementing seed, not a new record.

Rework consumes the original ConflictHandoff only after queue unwind, abort and serial slot release, using the original committed ticket text, findings and conflict context. The lock-owning ticket-plane writer applies only exact reviewed proposals without reacquiring its lock. Retain ReworkOrder, REWORK_ORDER, SUPERSEDES, cap_consumed, dead_dependency and all existing writers/shapes from the entry unit. Preserve publication-before-supersedes-before-retirement, producing-terminal-before-retirement, fresh Implement/Check/Review approvals, starting source/capability, effective call capability, lineage caps and all transitive successor dependency folds. Route diagnosis split and mechanical over-bound renders through reviewed Rework; spent/exhausted, reject and abandon-human keep their paths. Its explicit earned closure additions are chupa/runner.py, chupa/drain.py, chupa/scheduler.py, tests/test_ladder.py, tests/test_drain.py, tests/test_scheduler.py, tests/test_reject_queue.py and tests/test_diagnose.py. Migrate only the specified dormancy/split/over-bound assertions, preserving other assertions and inline admission. Re-grep at this merged authoring head for every further mechanically forced caller/negative assertion. Carry every entry-unit named invariant test, including proposal refusal/publication, fresh approval, caps, terminal order and transitive dependency tests, into the future Rework payload.

Create phase3-continue-07 as a medium/medium confirmed source: seed continuation depending on both merge-queue-activation and rework-activation. Its suffix is admissions[7:], its next payload is background-consumers and control-inbox, followed by phase3-continue-08 starting at admissions[8:]. The control-inbox seed explicitly depends on its background-consumers sibling as well as its seeder. The successor fences tickets plus only its own new tests/test_seeded_phase3_07.py and embeds the already merged tests/test_seeded_phase3_core.py as idiom, never this batch's new test. It cites 19.L, 19.I, 19.P3, section 13, 19.P3.background-consumers, 19.P3.control-inbox and section 20, plus complete entry units its own successor needs: 19.P3.dispatch-pause-boundary and 19.P3.pause-resume-activation. It requires before-writing gap-check/resolution of every needed entry unit and further required citation, with premise_failed naming missing/incomplete ids for section 11.4 hardening, never invented facts. Carry the same requirements for exact own-entry/row citations, closure greps, named invariant tests, exact record custody, Context partition and fixed authoring snapshots forward. Background/control construction remains behaviorally dormant; daemon import absence is no longer evidence after scheduler activation. Control requests and durable decisions retain the exact control-inbox shapes and one writer, with durable no-overwrite publication, lifecycle/hold binding and decision-before-mutation. Pause units govern its successor's next pair; do not author them in this batch.

Each continuation authors only its next admission and successor, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Each continuation depends on every payload of the previous admission and carries the shrinking suffix. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase. Never copy, alter, reorder, split, omit or rename registry rows or widen a fence without an earned closure path.

Create tests/test_seeded_phase3_06.py naming exactly merge-queue-activation, rework-activation and phase3-continue-07. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), all seeder/sibling edges, medium/medium starts, exact implementing own-entry/row citations, registry fence floors and only earned closure additions with reasons, complete activation transition closure, successor next-admission/next-seeder citations, its tickets/test fence and merged earlier idiom. Pin Context/On-demand closure and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Record the merged idiom and measurements. Every stuck budget fits drain.max_ticket_minutes. Name test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots and test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Never migrate historical seeding tests.

An approve holds on retry while bytes match its ticket_sha: keep previously approved seeds verbatim and re-author only snagged seeds. Leave all three new seeds uncommitted for Check to record each requisition_review verdict and lift all approved seeds together through one chupa(phase3-continue-06): seeds ticket-plane commit. Commit only this ticket's new test.

Out: Phase 3 implementation; payloads beyond merge-queue-activation, rework-activation and phase3-continue-07; Suggestion Box messages; plan/registry changes; existing tickets/run records and historical tests; tickets paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_06.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_06.py` exits 0 over exactly merge-queue-activation, rework-activation and phase3-continue-07, proving intake lint, confirmed seed birth, all seeder/sibling edges, medium/medium starts and stuck budgets within the drain envelope.
2. `uv run pytest -q tests/test_seeded_phase3_06.py` proves exact own-entry/row citations, fence floors with only recorded earned additions, complete activation transition closure, successor next-admission/next-seeder cites, tickets/test fence, merged earlier idiom, Context closure and maximum-effort render feasibility from fixed authoring snapshots.
3. At Check, `tickets/phase3-continue-06/checks.json` records requisition_review approve for all three seeds, lifted together through one chupa(phase3-continue-06): seeds ticket-plane commit. Leave seed files uncommitted; this branch commits only its new test.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_06.py
uv run pytest -q
```

## Definition of rejected
Reject registry copying/alteration, unearned fences, whole-phase/sibling implementation citations, invented facts, unnamed invariants, omitted negative fixtures or forced callers, out-of-admission payloads, box seeding, existing-ticket edits, code-branch ticket commits or any edit outside the fence. Missing/incomplete needed entry units return premise_failed naming their ids for section 11.4 hardening before regeneration. Within-admission consumption requires the sibling edge.

## Time budget
- expected: 60m
- stuck: 90m
