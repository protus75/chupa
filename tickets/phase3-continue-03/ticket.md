---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- rework-stage

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- 19.P3.thresh-runtime
- 19.P3.dispatch-admission-boundary
- 19.P3.dispatch-config-snapshot
- section 13

## Goal / Why
Advance the Phase 3 seeding chain by exactly one admission: author thresh-runtime and phase3-continue-04 as confirmed seeds, leaving both uncommitted for this ticket's Check to review and lift.

This is continuation 03. Its shrinking unseeded suffix is admissions[3:] of the YAML registry between BEGIN_REGISTRY_P3 and END_REGISTRY_P3 in CHUPA_PLAN.md, parsed directly from that file. The next admission is thresh-runtime alone; its successor continues at admissions[4:]. Never copy the registry into a repository file or alter its rows. tests/test_seeded_phase3_03.py owns this admission's historical structure and render pins; the already merged tests/test_seeded_phase3_core.py is the read-first idiom.

## Scope in / Scope out
In: before writing, parse the current registry, read the next row and its complete entry unit, and run entry_unit_gap and resolve_plan_contract for every entry unit either authored seed needs: 19.P3.thresh-runtime, 19.P3.dispatch-admission-boundary, and 19.P3.dispatch-config-snapshot. Read any further unit a required citation needs before emitting. Missing/thin units or needed omitted facts return premise_failed naming their ids for section 11.4 hardening; never invent a fact.

In: create thresh-runtime from its row and complete 19.P3.thresh-runtime entry unit only, depending on phase3-continue-03. Its deep: true row is evidence for high/high. Cite exactly 19.I, 19.P3.thresh-runtime, and section 6. Preserve the registry fence floor. Add only paths earned by 19.L closure rules 2-5, after grepping symbols and old recorded values across chupa/, eval/, and tests/, and record each addition's reason in this batch's test. Every fenced existing path is Context by default; move a path to On-demand only when recorded authoring-time measurements prove embedding it breaches headroom. Created paths belong in neither; prompt-specs and delimiter-bearing sources are never Context.

Name all entry-unit owners, records with exact shapes and writers, observables, and named test obligations. thresh.py owns session-local per-provider caps/FIFO waits, spill above SPILL_WAIT_SECONDS = 60, breaker signals/fold and pre-call refusal; providers.py owns dormant classification into the six closed failure classes; config.py retains the existing positive concurrency parser and breaker defaults. Construction is dormant: direct injected-seam tests only, no production caller/constructor changes, budget-accounting change, quota Timer, ordered failure-driven failover, alert, hold, box emission, cap draw or terminal writer. Preserve existing Effects replay, redaction, provider call/routing and abort behavior. Production wiring belongs to Phase 4's provider-cooldown-failover. Run every entry-unit preservation suite unchanged in Verification, without fencing or embedding it.

In: create phase3-continue-04 as a medium/medium confirmed source: seed continuation depending on thresh-runtime. Its shrinking suffix is admissions[4:], its next payload is dispatch-admission-boundary plus dispatch-config-snapshot, followed by phase3-continue-05. It fences tickets plus its own new tests/test_seeded_phase3_04.py, embeds an already merged earlier seeding test as idiom, and cites 19.L, 19.I, 19.P3, section 13, and all entry units its own two payloads and successor require. It reads and checks those units before writing. Realize the registry's within-admission dispatch-config-snapshot dependency on dispatch-admission-boundary explicitly. Each continuation authors only its next admission and successor under 19.L, at most seeding.max_seeds_per_admission including the tail. The chain ends at terminal phase3-exit as the sole payload with no successor; never seed past the next phase.

In: tests/test_seeded_phase3_03.py names only thresh-runtime and phase3-continue-04 and pins intake lint, confirmed seed birth, dependency edges, starting capability, exact own-entry-unit citations, registry fence floors and only earned closure additions, the successor's tickets/test fence and merged earlier idiom, Context/On-demand closure, recorded sizes, and maximum-effort base render feasibility. Render assertions use only authoring-time file sizes, ticket sizes, and plan-unit lengths recorded in that test, never live sizes or live plan lengths. A later rejected stamp is lifecycle history. Each seed's stuck budget fits drain.max_ticket_minutes. An approval holds on retry while bytes match its ticket_sha; keep previously approved seeds verbatim.

Out: implementing Phase 3 machinery; creating dispatch payloads or any seed beyond thresh-runtime and phase3-continue-04; Suggestion Box messages; editing existing tickets, plan, registry or merged historical tests; committing tickets paths on this code branch.

## Scope fence
- tickets
- tests/test_seeded_phase3_03.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_03.py` exits 0 over exactly thresh-runtime and phase3-continue-04, proving grammar-valid confirmed seed birth, stuck budgets within the drain envelope, thresh-runtime depending on phase3-continue-03 and the successor depending on thresh-runtime.
2. `uv run pytest -q tests/test_seeded_phase3_03.py` proves thresh-runtime's high/high start from its deep row, exact own-entry-unit cites, registry fence floor plus recorded closure additions, and the successor's medium/medium start, next-admission/next-seeder cites, tickets/test fence and merged earlier idiom. Context closure and maximum-effort base render feasibility use fixed authoring-time measurements recorded in that test.
3. At Check, `tickets/phase3-continue-03/checks.json` records requisition_review approve for both seeds, which reach main together through one chupa(phase3-continue-03): seeds ticket-plane commit. Leave both files uncommitted; this branch commits only its new seeding test and no tickets path.
4. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_03.py
uv run pytest -q
```

## Definition of rejected
Reject if any registry row is copied, changed, split, reordered, widened without an earned closure path, or omitted; an implementing seed cites the whole phase or another entry unit; a seed invents a fact; a seed is filed through the box, committed on the code branch, or authored beyond thresh-runtime and phase3-continue-04; or an edit leaves the fence. Missing/incomplete required units return premise_failed naming their ids for section 11.4 hardening before regeneration. A seed may depend on a sibling in its own batch under section 13.3.

## Time budget
- expected: 60m
- stuck: 90m
