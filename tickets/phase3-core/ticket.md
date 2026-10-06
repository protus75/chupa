---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: human
state: confirmed
---

## Depends on
- phase2-exit

## Context
- tests/test_seeded_phase2.py

## Plan contract
- 19.L
- 19.I
- 19.P3
- section 13

## Goal / Why
Phase 3 is seeded core-first from the `19.P3` registry under the per-ticket cite law (section 13): this ticket's Implement authors the registry's first admission, `daemon-scheduler` and `seed-successor-proof`, plus one `phase3-continue` seeding ticket, as `confirmed` `ticket.md` files left uncommitted for this ticket's Check to review and lift (19.L seeding chain). It replaces the merged `phase2-exit`'s seeding, which a merged stem cannot re-run (19.L operator recovery order).

Why: each implementing seed must read only its own entry unit, never the whole phase unit, so it is authored from the plan's facts instead of inventing them (19.L SPEC DEPTH).

Owners: `tests/test_seeded_phase3_core.py` owns this batch's seeding pins. The registry block `BEGIN_REGISTRY_P3` in `19.P3` is the ONE source the seeding reads, parsed straight from CHUPA_PLAN.md, never copied and never edited.

## Scope in / Scope out
- In: `tickets/daemon-scheduler/ticket.md` and `tickets/seed-successor-proof/ticket.md`. Each realizes exactly its registry row: `## Plan contract` `19.I`, its own entry unit (`19.P3.daemon-scheduler`, `19.P3.seed-successor-proof`), and each id its row's `cite` names; its row's `fence` as the `## Scope fence` floor; `## Depends on` `phase3-core`; `state: confirmed`, `source: seed`, `medium`/`medium` (neither row is `deep`); a stuck budget at or under `drain.max_ticket_minutes`. Every fact a seed states beyond its row comes from its entry unit; a fact the unit omits is a spec gap the seed path hardens (section 11.4), never invented.
- In: `tickets/phase3-continue/ticket.md`: the first continuation. It cites `19.L`, `19.I`, and `19.P3`; depends on both payloads; fences `tickets` plus its own new `tests/test_seeded_phase3_01.py`; embeds `tests/test_seeded_phase3_core.py` as its idiom; and authors the registry's next admission (`merge-queue`, `deep`, alone at `high`/`high`) plus `phase3-continue-02` carrying the shrinking unseeded suffix. It never authors past that admission.
- In: `tests/test_seeded_phase3_core.py` NAMES the three stems and asserts only over them (19.L SEEDING TESTS pin grain): intake lint passes, `source: seed` and `state: confirmed` as authored, stuck at or under `drain.max_ticket_minutes`, the `depends` edges above, each fence a superset of its row's floor, each implementing seed's `## Plan contract` naming its entry unit and never `19.P3`, and render feasibility computed from sizes and plan-unit lengths RECORDED IN THE TEST, never re-read live.
- Out: any Phase 3 machinery, any seed beyond the first admission and `phase3-continue`, any Suggestion Box message, any edit to an existing ticket, and any edit to the plan or its registry.

## Scope fence
- tickets
- tests/test_seeded_phase3_core.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_core.py` passes over exactly `daemon-scheduler`, `seed-successor-proof`, and `phase3-continue`.
2. At this ticket's Check, each of the three seeds receives a `requisition_review` `approve`, recorded in `tickets/phase3-core/checks.json`, and the three reach main in one `chupa(phase3-core): seeds` ticket-plane commit.
3. The branch's committed diff carries no `tickets/` path, so every seed reaches main only through the ticket-plane lift.
4. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_core.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A seed is filed through the Suggestion Box, committed on the branch, or authored past the first admission and `phase3-continue`.
- An implementing seed cites `19.P3` or another row's entry unit, or states a fact its entry unit omits.
- The registry is copied into a repo file, or a row is renamed, reordered, split, or widened beyond 19.L rules 2-5.
- The diff touches a file outside the fence.

## Time budget
- expected: 60m
- stuck: 120m
