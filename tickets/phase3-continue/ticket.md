---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- daemon-scheduler
- seed-successor-proof

## Context
- tests/test_seeded_phase2.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- 19.P3.merge-queue
- 19.P3.rework-stage
- section 13

## Goal / Why
Advance the Phase 3 seeding chain by exactly one admission: author merge-queue and phase3-continue-02 as confirmed seeds, leaving both uncommitted for this ticket's Check to review and lift.

This is continuation 01. The unseeded suffix is admissions[1:] of the YAML registry between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md, parsed directly from that file. Its next admission is merge-queue alone. Never copy the registry into a repository file or alter its rows. tests/test_seeded_phase3_01.py owns this admission's historical structure and render pins; the merged core test is the read-first idiom.

## Scope in / Scope out
- In: create merge-queue from its row and complete 19.P3.merge-queue entry unit only, citing 19.I, its own entry unit, section 9, and section 10, never 19.P3 or another row's entry unit. Depend on phase3-continue. Its deep row starts high/high, recording the row's deep: true as starting-capability evidence; keep its row's fence floor. Existing fenced paths are embedded Context unless recorded authoring-time measurements prove embedding breaches headroom, in which case use On-demand. Add only paths earned by 19.L closure rules 2-5 and record the reason for each addition in this batch's test. Preservation suites run unchanged in Verification without a fence or Context entry. Name the entry unit's owners, records, observables, and every named test obligation; invent no omitted fact. Construction stays dormant, including unchanged inline bootstrap admission; Rework consumption, daemon admission routing, inbox binding, and notification transport stay deferred.
- In: create phase3-continue-02 as a medium/medium confirmed source: seed continuation depending on merge-queue. Its suffix is registry admissions[2:], its next payload rework-stage alone at high/high, followed by phase3-continue-03. It fences tickets plus its own new tests/test_seeded_phase3_02.py, embeds the already merged tests/test_seeded_phase3_core.py as idiom, and cites 19.L, 19.I, 19.P3, and 19.P3.rework-stage. It carries its position and the shrinking registry suffix, reads and checks the entry units needed by the seeds it authors before writing, and authors only that next admission and successor. Each further continuation follows 19.L until the terminal phase3-exit admission has no successor.
- In: before authoring, check entry_unit_gap and resolve_plan_contract for every entry unit the two authored seeds must cite, including 19.P3.rework-stage. A missing/thin unit or needed omitted fact returns premise_failed naming the unit for section 11.4 hardening; never invent the fact. Parse the current registry rather than trusting a copied row. Each seed's stuck budget fits drain.max_ticket_minutes.
- In: tests/test_seeded_phase3_01.py names only merge-queue and phase3-continue-02 and pins lint, authored confirmed seed birth, dependencies, starting capability, fence floors and earned additions, own-entry-unit citations, Context/On-demand closure, recorded sizes, and max-effort render feasibility using only authoring-time measurements recorded in the test. A later rejected stamp is lifecycle history. No live file sizes or live plan lengths feed render assertions.
- Out: implementing Phase 3 machinery; creating rework-stage or any seed beyond this admission and its successor; Suggestion Box messages; editing existing tickets, plan, registry, or merged historical seeding tests; committing any tickets path on this branch.

## Scope fence
- tickets
- tests/test_seeded_phase3_01.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_01.py` exits 0 over exactly merge-queue and phase3-continue-02, with grammar-valid confirmed seed birth, stuck budgets within the drain envelope, merge-queue depending on phase3-continue, and the successor depending on merge-queue.
2. `uv run pytest -q tests/test_seeded_phase3_01.py` proves merge-queue's high/high start and exact own-entry-unit cites, its registry fence floor plus only recorded closure additions, and the successor's medium/medium start, next-admission cites, tickets/test fence, and merged earlier idiom. Context closure and maximum-effort base render feasibility use fixed authoring-time sizes and plan-unit lengths recorded in that test.
3. At Check, `tickets/phase3-continue/checks.json` records requisition_review approve for both seeds, which reach main together through one chupa(phase3-continue): seeds ticket-plane commit. Leave both files uncommitted; this branch's committed diff contains only its new seeding test, with no tickets path.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_01.py
uv run pytest -q
```

## Definition of rejected
Reject if a registry row is copied, changed, split, reordered, widened without an earned closure path, or omitted; an implementing seed cites the whole phase or another entry unit; a seed invents an entry-unit fact; a seed is filed through the box, committed on the code branch, or authored beyond merge-queue and phase3-continue-02; or an edit leaves the fence. Missing or incomplete required entry units return premise_failed naming their ids for section 11.4 hardening before regeneration.

## Time budget
- expected: 60m
- stuck: 120m
