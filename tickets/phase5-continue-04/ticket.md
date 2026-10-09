---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- status-projection
- baseline-binding-reader

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.I
- 19.P5
- 19.P5.retro-doctor-cli
- section 18
- section 13

## Goal / Why
Check admits the operator retro/doctor contract and the terminal Phase 5 continuation.

## Scope in / Scope out
Read the committed BEGIN_REGISTRY_P5/END_REGISTRY_P5 YAML in its original order. Position 04 carries admissions[4:]; author exactly retro-doctor-cli and phase5-continue-05. Remaining suffix: [retro-doctor-cli], [phase5-exit]. Carry position 05 and admissions[5:] into phase5-continue-05, whose fence is only tickets and tests/test_seeded_phase5_05.py and whose Context embeds merged tests/test_seeded_phase3_core.py. This admission's batch test is tests/test_seeded_phase5_04.py, never its own Context. The last admission authors only phase5-exit without a successor. Do not emit phase5-exit here.

retro-doctor-cli depends on phase5-continue-04. phase5-continue-05 depends on retro-doctor-cli, consuming every preceding admission payload. Preserve all registry consumption edges and refuse forward edges. Unmarked rows and continuations start medium/medium; only a registry deep: true row starts KNOWN-DEEP high/high and occupies its admission alone. phase5-exit starts KNOWN-HARD high/high on 19.L evidence. Do not split, rename, add or reorder registry rows.

Before authoring any seed, resolve_plan_contract resolves every role, entry and row citation; required_units and entry_unit_gap validate all required non-exit entries for both seeds. Read their Owner, Records, Observable and Tests. Missing or contradictory facts return premise_failed, kind: spec_gap naming the owning unit. retro-doctor-cli cites 19.I, 19.P5.retro-doctor-cli and section 18. phase5-continue-05 cites 19.L, 19.I, 19.P5, 19.P6 and section 13 for its terminal exit admission. Cite ids only; never copy entry prose or section 19. Source new chupa/doctor.py ownership from the cited entry.

Named next-entry obligations: test_retro_doctor_entry_unit, test_retro_no_merge, test_retro_success, test_retro_no_commit, test_retro_refusals, test_doctor_check_order, test_doctor_failures, test_doctor_is_read_only, test_doctor_cli. Create the entry test in tests/test_cli.py and new doctor tests in tests/test_doctor.py, their entry owners; future tests never enter Context. The entry test covers required_units, one resolve_plan_contract heading and all entry_unit_gap parts for the row and this continuation; test_plan_lint stays green. Preserve scorecard, retro recovery/suppression/provenance/proposals, status and baseline assertions. Leave the phase exit to its terminal admission.

Apply 19.L rules 2-5 by reading predecessor owners and scanning signatures, callers, compositions, operation allowlists and negative assertions across chupa/, eval/ and tests/. The registry fence is a floor; pin each earned addition with the exact caller or contradicted assertion that requires it. If criteria force an unearned path, return premise_failed for contract repair. Embed existing fenced paths in Context by default; On-demand requires measured overflow of 300,000 characters. Created files, same-admission sibling creations, prompt specs and delimiter-bearing sources stay outside Context. Unchanged preservation suites belong only in Verification.

Pin the two seeds, grammar, confirmed source: seed birth, edges, role citations, required depths, named obligations, tier evidence, earned closure, finite shrinking suffix, caps and budgets in tests/test_seeded_phase5_04.py. Snapshot authoring head, merged idiom blob, entry hashes, cited-unit lengths, and file/ticket bytes and characters. Fixed maximum-effort render arithmetic never reads live file sizes or live plan lengths. Preserve immutable historical fixtures. Bound every admission including the successor by seeding.max_seeds_per_admission and each stuck budget by drain.max_ticket_minutes.

Write new seeds directly and leave them uncommitted; only the new batch test is committed on the code branch. Check performs requisition_review, records approvals in tickets/phase5-continue-04/checks.json before a single ticket-plane seed lift. Retain approved bytes while ticket_sha matches; re-author only snagged seeds. No production edits, existing ticket/run-record edits, plan edits, Box messages, manual release or additional payloads.

## Scope fence
- tickets
- tests/test_seeded_phase5_04.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase5_04.py` exits 0 proving exactly retro-doctor-cli and phase5-continue-05, grammar, birth, citations, consumption, closure, depths, named tests, finite suffix and fixed render feasibility.
2. `tickets/phase5-continue-04/checks.json` records requisition_review approvals before one seed lift; only the batch test is committed on the code branch.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving predecessor behavior and historical snapshots.

## Verification
```
uv run pytest -q tests/test_seeded_phase5_04.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap and the owning cited unit; a criteria-forced path outside earned closure needs contract repair.

## Time budget
- expected: 60m
- stuck: 180m
