---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- merge-queue

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- 19.P3.rework-stage
- 19.P3.thresh-runtime
- section 13

## Goal / Why
Advance the Phase 3 seeding chain by exactly one admission: author rework-stage and phase3-continue-03 as confirmed seeds, leaving both uncommitted for this ticket's Check to review and lift.

This is continuation 02. Its shrinking unseeded suffix is admissions[2:] of the YAML registry between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md, parsed directly from that file. The next admission is rework-stage alone. Never copy the registry into a repository file or alter its rows. tests/test_seeded_phase3_02.py owns this admission's historical structure and render pins; the already merged tests/test_seeded_phase3_core.py is its read-first idiom.

## Scope in / Scope out
In: before writing, parse the current registry and read its next row and complete entry unit. Run entry_unit_gap and resolve_plan_contract for every entry unit either authored seed must cite, including 19.P3.rework-stage and 19.P3.thresh-runtime. A missing/thin unit or a needed omitted fact returns premise_failed naming the unit for section 11.4 hardening; never invent a fact.

In: create rework-stage from its registry row and complete 19.P3.rework-stage entry unit only. It depends on phase3-continue-02. Its deep: true row supplies starting-capability evidence for high/high. Cite exactly 19.I, 19.P3.rework-stage, section 4, section 9, and section 11, never the whole phase or another row's entry unit. Keep its fence floor. Embed every fenced existing path in Context unless recorded authoring-time measurements prove embedding breaches headroom, then use On-demand. A created path is in neither. Prompt-spec files are never Context; specs/rework.md is a future fenced output governed by its entry unit. Add only paths earned by 19.L closure rules 2-5 and record each reason in this batch's test. Run unchanged preservation suites in Verification without fencing or embedding them.

Name the entry unit's owners, every record with its shape and writer, observables, and all named test obligations. Construction stays dormant: Rework is called directly through the existing Driver and returns reviewed update/split/escalate orders without ticket mutation; the separate supersedes writer runs only after successor publication. A typed ConflictHandoff is consumed only after admission aborts and releases its serial boundary, with approval invalidated. Preserve the bootstrap inline admission and production split-to-Reject routing. Production consumption and ticket-plane application stay deferred to rework-activation. Do not implement machinery in this seeding ticket.

In: create phase3-continue-03 as a medium/medium confirmed source: seed continuation depending on rework-stage. Its shrinking suffix is registry admissions[3:], its next payload thresh-runtime alone at high/high followed by phase3-continue-04. It fences tickets plus its own new tests/test_seeded_phase3_03.py, embeds an already merged earlier seeding test as idiom, and cites 19.L, 19.I, 19.P3, and the entry units its two authored seeds need. It reads and checks those units before writing and authors only that admission and successor. Each continuation follows 19.L until terminal phase3-exit is the sole payload with no successor. Never seed past the next phase.

In: tests/test_seeded_phase3_02.py names only rework-stage and phase3-continue-03 and pins intake lint, authored confirmed seed birth, dependencies, starting capability, registry fence floors and earned additions, own-entry-unit citations, Context/On-demand closure, recorded sizes, and maximum-effort base render feasibility. Every render assertion uses only authoring-time file sizes, ticket sizes, and plan-unit lengths recorded in that test; no live sizes or live plan lengths. A later rejected stamp is lifecycle history. Each seed's stuck budget fits drain.max_ticket_minutes. An approval holds on retry while its bytes match, so keep previously approved seeds verbatim.

Out: implementing Phase 3 machinery; creating thresh-runtime or seeds beyond this admission and its successor; Suggestion Box messages; editing existing tickets, plan, registry, or merged historical tests; committing tickets paths on this branch.

## Scope fence
- tickets
- tests/test_seeded_phase3_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_02.py` exits 0 over exactly rework-stage and phase3-continue-03, with grammar-valid confirmed seed birth, stuck budgets within the drain envelope, rework-stage depending on phase3-continue-02, and its successor depending on rework-stage.
2. `uv run pytest -q tests/test_seeded_phase3_02.py` proves rework-stage's high/high start, exact own-entry-unit cites, registry fence floor plus only recorded closure additions, and the successor's medium/medium start, next-admission cites, tickets/test fence, and merged earlier idiom. Context closure and maximum-effort base render feasibility use fixed authoring-time sizes and plan-unit lengths recorded in that test.
3. At Check, `tickets/phase3-continue-02/checks.json` records requisition_review approve for both seeds, which reach main together through one chupa(phase3-continue-02): seeds ticket-plane commit. Leave both files uncommitted; this branch's committed diff contains only its new seeding test, with no tickets path.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_02.py
uv run pytest -q
```

## Definition of rejected
Reject if a registry row is copied, changed, split, reordered, widened without an earned closure path, or omitted; an implementing seed cites the whole phase or another entry unit; a seed invents an entry-unit fact; a seed is filed through the box, committed on the code branch, or authored beyond rework-stage and phase3-continue-03; or an edit leaves the fence. Missing or incomplete required entry units return premise_failed naming their ids for section 11.4 hardening before regeneration. A seed may depend on a sibling seed of its own batch (section 13.3).

## Time budget
- expected: 60m
- stuck: 120m
