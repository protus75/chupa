---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- remove-plan-gap-hardening

## Context
- chupa/merge.py
- docs/how-chupa-works.md

## On-demand
- chupa/stages.py
- chupa/mergequeue.py
- chupa/config.py
- chupa/tickets.py
- docs/host-contract.md
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_seed_path.py
- tests/test_stages.py

## Goal / Why
"Seeding" let a ticket whose `## Scope fence` includes `tickets` write new `source: seed` tickets: Check reviewed each seed with `requisition_review`, lifted the approved ones as `chupa(<stem>): seeds`, and a merge gate re-checked their approvals. It existed only to let the bootstrap plan write its own phase tickets. That is finished, every seeding ticket is settled, and nothing should create tickets this way again. After this change no run reviews, lifts, or gates seeds; tickets are written by people or by the Author stage only.

## Scope in / Scope out
- In: `chupa/stages.py`: delete `APPROVED_SEEDS`, `VERDICT_SIGNAL`, `_seed_verdicts`, `_prior_review`, `_restore_approved_seeds`, `_seeded_stems`, `_prior_seed_reviews`, `_review_seeds`, `_review_one`, `lift_seeds`; the seeding branch of `check`; the approved-seed restore in `implement` and the `kept` parameter of `implement_stage`; imports left unused.
- In: `chupa/stages.py` keeps `SeedReview` and `Invoice.seeds` (default empty), with a comment saying why: 245 lifted `checks.json` files carry a `seeds` key (51 non-empty), and `retro.py` and `triage.py` parse old `checks.json` from git history through `Invoice`, which refuses unknown keys.
- In: `chupa/merge.py`: delete `SeedSafetyGate`, `SeedOnMain`, `gather_seeds`, `Candidate.seeds` and `Candidate.seed_checks_text`, the seeds/checks parameters of `read_candidate`, and the `requisition_review` severity bump; `MERGE_GATES` drops `SeedSafetyGate`; `AdmissionBoundary` runs `PostRebaseGate` alone. The `requisition_review` gate code stays (Author and Rework use it).
- In: `chupa/mergequeue.py`: drop the `gather_seeds` call, the seeds/checks arguments, and the severity bump.
- In: `chupa/config.py`: delete `Seeding` and the `seeding` field.
- In: drop the `siblings` parameter (only seeding passes it): `parse_ticket` and `validate_ticket` in `chupa/tickets.py`, `review_target` and `review_ticket` in `chupa/requisition.py`. Rework writes its proposals into a scratch checkout, so their sibling dependencies resolve from disk without it.
- In: `chupa/tickets.py`: `source: seed` stays valid (236 committed tickets carry it); the new-stem refusal's text stops naming "phase seeding" (only the machine writes `seed` or `box:<class>`; machine work enters through the Suggestion Box).
- In: tests. Delete `tests/test_seed_path.py` and `tests/test_seed_successor.py`. In `tests/test_merge.py`, delete `seed_reviewed`, `test_merge_safety_refuses_a_seed_whose_committed_blob_changed`, `test_merge_safety_rechecks_seed_lint_even_with_a_matching_approval`, `test_merge_safety_admits_a_seed_with_matching_recorded_approval`, `test_merge_safety_reads_committed_seed_and_checks_despite_dirty_main_checkout`, and the `tests.test_seed_path` import; `test_daemon_prechecks_precede_offer` keeps only its `ticket-plane` case, rebuilt on this file's non-seed fixtures. In `tests/test_mergequeue.py`, delete `test_committed_seed_approval_preserved` and the `requisition_review` case of `test_safety_failure_skips_integration`. Delete `test_seed_review_without_plan` from `tests/test_no_plan_host.py` and `test_exit_receipt_entry_unit` from `tests/test_host_loop.py`. In `tests/test_closed_sets.py`, `MERGE_GATES` drops `SeedSafetyGate`. In `tests/test_config.py`, drop the `seeding` assertion. `tests/test_stages.py` keeps its old-`checks.json` parse test.
- In: `tests/test_serve.py` `test_serve_conflict_handoff_runs_after_admission_unwinds`: drop both trailing `"requisition_review"` entries from the expected `gates` list (`SeedSafetyGate` no longer runs).
- In: `tests/test_hostfiles.py`: delete `test_core_activation_entry_unit` (it parses the committed `tickets/core-drift-activation/ticket.md`, whose `## On-demand` names the deleted `tests/test_seed_path.py` and `tests/test_seed_successor.py`) and the imports only it uses.
- In: add `test_old_checks_json_with_seed_reviews_still_parses` to `tests/test_stages.py`: an `Invoice` JSON carrying one non-empty `seeds` entry (as committed by a past seeding run) parses (it fails if `seeds` or `SeedReview` is removed or made stricter).
- In: `docs/how-chupa-works.md`: section 3.1 says `source: seed` marks tickets written by the finished bootstrap and nothing writes it now; section 5.1 drops the `requisition_review` merge-gate row; section 13 drops the seeding bullet. `docs/host-contract.md`: drop `seeding` from the config schema and examples; keep `seed` in the source list, marked historical.
- Out: `Finding.kind`/`unit` (old artifacts carry them), `SeedReview`/`Invoice.seeds`, `source: seed` validity, the `requisition_verdict` signal (Author writes it), the `requisition_review` gate code, ticket grammar and `_seed_cites`, `CHUPA_PLAN.md`.

## Scope fence
- chupa/stages.py
- chupa/merge.py
- chupa/mergequeue.py
- chupa/config.py
- chupa/tickets.py
- chupa/requisition.py
- tests/test_seed_path.py
- tests/test_seed_successor.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_no_plan_host.py
- tests/test_host_loop.py
- tests/test_closed_sets.py
- tests/test_config.py
- tests/test_stages.py
- docs/how-chupa-works.md
- docs/host-contract.md
- tests/test_serve.py
- tests/test_hostfiles.py

## Acceptance criteria
1. `grep -rn -E "SeedSafetyGate|gather_seeds|lift_seeds|_review_seeds|_review_one|APPROVED_SEEDS|max_seeds_per_admission" chupa` prints nothing.
2. An old `checks.json` with a non-empty `seeds` list still parses as an `Invoice` (not refused), checked by `uv run pytest tests/test_stages.py -k old_checks_json_with_seed_reviews`.
3. `docs/how-chupa-works.md` has no seeding bullet in section 13 and no `requisition_review` merge-gate row.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_stages.py -k old_checks_json_with_seed_reviews
uv run pytest -q
```

## Definition of rejected
`Invoice.seeds`, `SeedReview`, `Finding.kind`/`unit`, or `source: seed` validity is removed; any committed `checks.json` or ticket file is edited; `CHUPA_PLAN.md` changes.

## Time budget
- expected: 60m
- stuck: 90m
