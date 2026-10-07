---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- thresh-runtime

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- 19.P3.dispatch-admission-boundary
- 19.P3.dispatch-config-snapshot
- 19.P3.scheduler-activation
- 19.P3.merge-queue-activation
- 19.P3.rework-activation
- section 13

## Goal / Why
Advance Phase 3 by exactly one admission: author dispatch-admission-boundary, dispatch-config-snapshot and phase3-continue-05 as confirmed seeds, left uncommitted for this ticket's Check to review and lift together. This is continuation 04. Parse the YAML registry directly between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md; its shrinking unseeded suffix is admissions[4:]. Its next payload is the two dispatch rows alone and its successor starts at admissions[5:]. Never copy the registry into a repository file or alter its rows.

## Scope in / Scope out
Before writing, parse the current registry, read both next rows and their complete entry units, and run entry_unit_gap and resolve_plan_contract for every entry unit either authored payload or successor needs: 19.P3.dispatch-admission-boundary, 19.P3.dispatch-config-snapshot, 19.P3.scheduler-activation, 19.P3.merge-queue-activation and 19.P3.rework-activation. Read any further unit a needed citation requires. Missing/thin units or omitted needed facts return premise_failed naming their ids for section 11.4 hardening; never invent facts.

Create dispatch-admission-boundary and dispatch-config-snapshot only from their registry rows and complete own-entry units, both medium/medium and depending on phase3-continue-04. Realize the within-admission dependency explicitly: dispatch-config-snapshot also depends on dispatch-admission-boundary. The admission seed cites exactly 19.I, 19.P3.dispatch-admission-boundary and section 9; the snapshot seed cites exactly 19.I, 19.P3.dispatch-config-snapshot and section 15, never the phase unit or a sibling entry unit. Preserve each registry fence floor. Add only paths earned by 19.L closure rules 2-5, after grepping symbols and old assertion values across chupa/, eval/ and tests/, and record each addition and its reason in this batch's test. Existing fenced paths are Context by default; On-demand requires recorded authoring-time measurements proving embedding breaches headroom. Created paths belong in neither. Prompt-specs and delimiter-bearing sources are never Context. A sibling-created daemon.py is not Context for the snapshot seed; construction must read it after the dependency merges. Keep preservation suites unchanged, Verification-only, neither fenced nor embedded.

Name every entry-unit owner, exact record shape and writer, observable and named test obligation in each payload. chupa/daemon.py owns DaemonAdmission around the existing Dispatch callback: serial slot before task creation, original Ticket and terminal unchanged, memory-only active/task ownership, cleanup complete before slot release, cancellation of a waiter leaves the active task untouched, and active cancellation awaits cleanup. It selects no tickets and writes no accounting or terminal. chupa/config.py owns snapshot_config(config), the detached recursively immutable view of every Python-mode config dump field with attribute access, read-only mappings and tuple sequences. chupa/daemon.py owns snapshot_dispatch(load, bind), captured inside the admission slot, once per call; edits affect only the next admission and invalid reload has no stale fallback. The loader remains the only parser. Both are dormant constructions; direct injected-seam tests and real CLI raising probes prove no production caller, plus the transitive CLI import-closure scan recognizing both import idioms. No existing public signature, constructor or production caller changes. Scheduler activation later owns wiring and dormancy migration. Run every entry-unit preservation suite unchanged in Verification without fencing or embedding it.

Create phase3-continue-05 as a medium/medium confirmed source: seed continuation depending on BOTH dispatch payloads. Its suffix is admissions[5:], its next payload is scheduler-activation alone, followed by phase3-continue-06 starting at admissions[6:]. It fences tickets plus only its own new tests/test_seeded_phase3_05.py and embeds an already merged earlier seeding test as idiom (tests/test_seeded_phase3_core.py), never this batch's new test. It cites exactly 19.L, 19.I, 19.P3, section 13, 19.P3.scheduler-activation, 19.P3.merge-queue-activation and 19.P3.rework-activation. It reads and gap-checks/resolves all three of those entry units before writing, and reads any further required citation. These activation units now govern its next-admission/next-seeder contract: scheduler-activation builds the real production core and composition harness, and the successor continuation authors merge-queue-activation and rework-activation with their explicit sibling dependency. Do not author any activation payload in this batch.

Each continuation authors only its next admission and successor under 19.L, at most seeding.max_seeds_per_admission including the tail. Deep rows start high/high; other rows medium/medium. Row fences remain floors with only earned closure additions; activation fences every predecessor dormancy/negative fixture and composition caller its flip forces. Each continuation depends on every payload of the previous admission and carries the next shrinking suffix. The chain ends at terminal phase3-exit as its sole payload with no successor; never seed past the next phase.

Create tests/test_seeded_phase3_04.py naming exactly the three seeds. Pin grammar-valid confirmed seed birth (a later rejected stamp is lifecycle history), dependencies including the explicit sibling edge and both successor edges, medium/medium starts, exact own-entry-unit citations, registry fence floors and only earned closure additions with reasons, and the successor's exact citation set, tickets/test fence and merged earlier idiom. Pin Context/On-demand closure, authoring-time sizes and maximum-effort base render feasibility using only file sizes, ticket sizes and plan-unit lengths recorded IN that test, never live sizes or live plan lengths. Every stuck budget fits drain.max_ticket_minutes. Use the named obligations test_named_stems_cover_exactly_this_admission_and_successor, test_seed_passes_intake_lint_with_confirmed_seed_birth, test_stuck_budget_fits_the_drain_envelope, test_dependencies_as_authored, test_fence_contains_its_floor_and_only_earned_additions, test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract, test_successor_cites_next_admission_and_embeds_merged_earlier_idiom, test_context_closure_and_max_effort_render_use_authoring_snapshots, and test_payloads_run_preservation_suites_without_fencing_or_embedding_them. Record a merged idiom and authoring measurements; do not migrate earlier historical seeding tests.

An approve holds on retry while bytes match its ticket_sha; keep previously approved seeds verbatim and re-author only snagged seeds. Check records each requisition_review verdict and lifts all three approved seeds together through the ticket-plane lane. Commit only this ticket's new test, leaving all new tickets files uncommitted.

Out: Phase 3 machinery implementation; any payload beyond the two dispatch seeds and phase3-continue-05; Suggestion Box messages; plan/registry changes; editing existing tickets, run records or historical tests; tickets paths in this code-branch commit.

## Scope fence
- tickets
- tests/test_seeded_phase3_04.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_04.py` exits 0 over exactly dispatch-admission-boundary, dispatch-config-snapshot and phase3-continue-05, proving intake lint, confirmed seed birth, stuck budgets within the drain envelope and all dependency edges, including dispatch-config-snapshot consuming its admission sibling and the successor depending on both payloads.
2. `uv run pytest -q tests/test_seeded_phase3_04.py` proves medium/medium starts, exact implementing own-entry/row citations, registry fence floors with only recorded earned closure additions, successor next-admission/next-seeder cites, its tickets/test fence and merged earlier idiom, Context closure and maximum-effort base render feasibility using fixed authoring snapshots.
3. At Check, `tickets/phase3-continue-04/checks.json` records requisition_review approve for all three seeds, which reach main together through one chupa(phase3-continue-04): seeds ticket-plane commit. Leave new seed files uncommitted; this branch commits only its new test and no tickets path.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_04.py
uv run pytest -q
```

## Definition of rejected
Reject if a registry row is copied, altered, reordered, renamed, split, omitted or widened without an earned closure path; a payload cites the whole phase or another entry unit; a seed invents a fact, lacks a named invariant test, is filed through the box, is committed on the code branch or is authored past this admission; or an edit leaves the fence. Missing/incomplete needed entry units return premise_failed naming their ids for section 11.4 hardening before regeneration. A seed may depend on a sibling in its own batch under section 13.3.

## Time budget
- expected: 60m
- stuck: 90m
