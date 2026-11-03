---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- review-spec-readonly
- implement-consumer-read

## Context
- tests/test_seeded_phase6_01.py

## Plan contract
- 19.L
- 19.I
- 19.P7
- section 13
- 19.P7.host-mechanical-check
- section 7
- section 8

## Goal / Why
Advance Phase 7 by authoring its host mechanical payload and the next continuation, keeping the remaining registry obligations in the same drain.

## Scope in / Scope out
This is the seeding role at Position 1, carrying admissions[1:] from the committed Phase 7 registry. Parse BEGIN_REGISTRY_P7/END_REGISTRY_P7 YAML from the plan directly; keep it out of source files. The remaining admissions are host-mechanical-check, then host-review-surfaces, then phase7-exit alone.

Author exactly host-mechanical-check and phase7-continue-02. The payload depends on phase7-continue and both registry prerequisites, review-spec-readonly and implement-consumer-read. The successor depends on host-mechanical-check, carries position 2 and admissions[2:], and cites the seeding-role units and the host-review-surfaces entry with its row citations. Its Context uses a merged earlier seeding test, never a test newly created by its admission. Admit no host-review-surfaces or exit payload now; refuse forward edges.

Resolve every proposed role, registry-row citation and required entry with resolve_plan_contract before writing seeds. Use required_units and entry_unit_gap for every non-exit entry the payload and successor need, including host-review-surfaces. Inspect Owner, Records, Observable and Tests before grammar and before review. A missing or contradictory governing fact stops with premise_failed, kind: spec_gap and its owning unit; do not supply missing facts in ticket prose. Cite plan ids under Plan contract without copying the cited text into bodies.

Host mechanical execution stays owned by chupa/stages.py at Check and chupa/merge.py at inline merge. Author the complete cited host-mechanical-check contract, carrying every named test obligation, with no production implementation here. Read the merged owners and their tests first. Use the row fence as a floor and apply 19.L rules 2-5 across chupa/, eval/ and tests/. Record each earned addition's exact direct caller or contradicted assertion in the admission snapshot. Preserve historical seeding fixtures unchanged.

Use medium/medium for ordinary payloads and continuations. A deep: true row is alone at high/high; the exit is KNOWN-HARD high/high. Bound the whole batch, successor included, by seeding.max_seeds_per_admission, and stuck budgets by drain.max_ticket_minutes. Do not change registry names, row order, admission boundaries or obligations. The terminal phase7-exit is the only payload in its admission, has no successor in Phase 7, and authors the 19.P8 core.

Embed existing fenced files as Context by default; prompt specs and delimiter-bearing sources never enter Context. Move an existing path to On-demand only when its recorded embedding exceeds headroom. Include no future path in either input section. Snapshot the authoring head, merged idiom blob, entry hashes, citation lengths, ticket and file bytes and characters, required-unit depth and missing-part rejection. Pin grammar, seed birth, exact stems, edges, tiers, fences, Context partition, position and shrinking suffix. Measure the maximum-effort base Implement render from recorded operands alone.

Both seeds are already on main: an earlier attempt of this stem lifted host-mechanical-check and phase7-continue-02, and the operator then corrected host-mechanical-check to the repaired 19.P7.host-mechanical-check entry (host check codes are not gate_bypass codes; ticket validation is unchanged). Treat both as this stem's own emitted seeds: do not rewrite either file. Write and commit only tests/test_seeded_phase7_01.py, pinning the committed bytes of both seeds. Check runs requisition_review for each seed whose bytes differ from its approved ticket_sha (the corrected host-mechanical-check) and records the verdict in this ticket's checks.json; phase7-continue-02's approval holds while its bytes match. Review, approval records and lifting belong to Check. Do not enqueue Box messages, perform a manual release, implement production behavior or seed beyond this admission.

## Scope fence
- tickets
- tests/test_seeded_phase7_01.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase7_01.py` exits 0 with test_phase7_01_exact_admission pinning exactly host-mechanical-check and phase7-continue-02, confirmed seed birth, row and seeder dependencies, role citations, medium/medium tiers, position 2 and admissions[2:], the batch cap, stuck budgets and absence of forward edges.
2. `uv run pytest -q tests/test_seeded_phase7_01.py` exits 0 with test_phase7_01_entry_depth checking required_units for payload and successor, unique resolve_plan_contract resolution and all entry_unit_gap parts with missing-part rejection; the host mechanical payload carries every named Tests obligation of its entry.
3. `uv run pytest -q tests/test_seeded_phase7_01.py` exits 0 with test_phase7_01_closure and test_phase7_01_render pinning earned fence additions, recorded Context/on-demand sizes, entry hashes and citation lengths, and maximum-effort render feasibility from recorded operands. Both seeds stay as committed on main; Check records requisition_review verdicts in checks.json for any seed whose bytes changed since approval.
4. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 while historical snapshots remain unchanged.

## Verification
```
uv run pytest -q tests/test_seeded_phase7_01.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A governing omission or contradiction returns premise_failed with kind: spec_gap and the owning unit. A forced edit beyond earned fence closure requires contract repair. Never invent plan facts or admit a later payload.

## Time budget
- expected: 60m
- stuck: 90m
