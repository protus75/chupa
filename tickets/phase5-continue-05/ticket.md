---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- retro-doctor-cli

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P5
- 19.P6
- section 13

## Goal / Why
Check admits the terminal Phase 5 exit after every feature payload has merged.

## Scope in / Scope out
Read committed BEGIN_REGISTRY_P5/END_REGISTRY_P5 YAML in original order. Position 05 carries admissions[5:], the sole remaining suffix [phase5-exit]. Author exactly phase5-exit without a successor; never re-emit an earlier row, split, rename, add or reorder rows. The exit seed depends on phase5-continue-05 and transitively consumes every preceding admission payload. Preserve registry consumption edges and refuse forward edges. Phase5-exit starts KNOWN-HARD high/high on 19.L evidence; unmarked rows and continuations start medium/medium, only deep: true rows start KNOWN-DEEP high/high and occupy an admission alone.

Before writing, resolve_plan_contract resolves all role, entry and row citations. required_units and entry_unit_gap validate all required non-exit entries, including the Phase 6 core entry units the exit seed will cite; read Owner, Records, Observable and Tests. A missing or contradictory fact returns premise_failed, kind: spec_gap naming its owning cited unit. Cite ids only; never copy section 19 or entry prose. The exit cites 19.L, 19.I, 19.P5, 19.P6, section 13 and every entry unit needed to author the 19.P6 core admission. It authors that core and its continuation only, never seeds past the next phase.

The exit acceptance criteria name transitive-dependency coverage and each Phase 5 exit read from 19.P5 with its emitter deliverable. Use the latest committed real retro receipt produced by the forced pre-exit hook after the final feature merge, not fixture evidence or a hand-written report. Its tests must prove scorecard, spend/tokens, existing surfaces and stems, zero escapes and real production provenance. Read merged tests for the retro-box chain and baseline reader, retaining the entry's committed approval evidence. Follow 19.L's committed-artifact and wired-and-shaped exit evidence laws; never require live ignored state in a clean checkout. An unmet read returns premise_failed naming it. Do not implement the exit or generate Phase 6 payloads in this admission.

Apply 19.L rules 2-5: read predecessor owners and scan signatures, callers, compositions, operation allowlists and negative assertions across chupa/, eval/ and tests/. The registry fence is a floor. Record each earned addition with the exact caller or contradicted assertion; an unearned forced path needs contract repair. Embed existing fenced paths in Context by default; On-demand requires measured overflow of 300,000 characters. Created files, same-admission sibling creations, prompt specs and delimiter-bearing sources never enter Context. Preservation suites belong only in Verification. The exit owns its new tests/test_phase5_exit.py and tests/test_seeded_phase6_core.py; future tests never enter Context.

Pin the sole seed, grammar, confirmed source: seed birth, role citations, edges, required depths, named exit reads and Phase 6 core test obligations, tier evidence, earned closure and terminal finite suffix in tests/test_seeded_phase5_05.py. Snapshot authoring head, merged idiom blob, entry hashes, cited-unit lengths and file/ticket bytes and characters. Fixed maximum-effort render arithmetic never reads live file sizes or live plan lengths. Preserve immutable historical fixtures. Bound every admission including a successor by seeding.max_seeds_per_admission and every stuck budget by drain.max_ticket_minutes. This batch has one seed and no successor. Use merged tests/test_seeded_phase3_core.py as the idiom, never this admission's test as Context. test_plan_lint stays green.

Write the new seed directly and leave it uncommitted; only the new batch test is committed on the code branch. Check performs requisition_review, records approvals in tickets/phase5-continue-05/checks.json before a single ticket-plane seed lift. Retain approved bytes while ticket_sha matches; re-author only snagged seeds. No production edits, existing ticket/run-record edits, plan edits, Box messages, manual release or additional payloads.

## Scope fence
- tickets
- tests/test_seeded_phase5_05.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase5_05.py` exits 0 proving exactly phase5-exit without a successor, grammar, birth, citations, consumption, closure, required depths, named exit/core obligations, high/high evidence and fixed render feasibility.
2. `tickets/phase5-continue-05/checks.json` records requisition_review approvals before one seed lift; only the batch test is committed on the code branch.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving predecessor behavior and historical snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase5_05.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap and the owning cited unit; an exit read without a real emitter or a criteria-forced path outside earned closure needs contract repair.

## Time budget
- expected: 60m
- stuck: 180m
