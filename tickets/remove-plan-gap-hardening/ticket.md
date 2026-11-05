---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- prompts-drop-plan

## Context
- chupa/hardening.py
- chupa/caps.py
- chupa/journal.py
- docs/how-chupa-works.md

## On-demand
- chupa/runner.py
- chupa/drain.py
- chupa/config.py
- docs/host-contract.md
- tests/test_drain.py
- tests/test_seed_path.py
- tests/test_daemon_composition.py
- tests/test_reject_queue.py
- tests/test_closed_sets.py
- tests/test_config.py

## Goal / Why
When a ticket fails with a `spec_gap` finding, chupa holds it and files a `plan-gap-<n>` ticket that edits `CHUPA_PLAN.md`, then releases the hold when that ticket merges or the plan's bytes change. The plan is a frozen history record and must never be edited again, so this machinery can only do harm. After this change chupa never holds a stem for a spec gap, never files a plan-gap ticket, never reads the plan to release a hold, and no operator message tells anyone to fix the plan.

## Scope in / Scope out
- In: delete `chupa/hardening.py`.
- In: `chupa/runner.py`: delete the spec-gap block in `drive` (the `gaps` dict and its `hold_on_hardening` call), `hold_on_hardening`, `hardening_text`, `file_hardening`, `SPEC_GAP_HOLD`, and the imports only they use. In `verdict`, delete the `plan_units` re-keep branch; the refusal's road becomes "edit the ticket before re-enqueueing".
- In: `chupa/drain.py`: delete `awaited_hardening`, the closed-hardener exclusion in `_select`, plan-bound release (`_Scan.plan_changed`, the committed-plan read in `_scan`, the plan file in `_offer_material`, every `plan_units` branch in `_select`, `_run_one`, and `_settle`), and the spec-gap hold in `premise_parked` and `_run_one`. `premise_parked` keeps only the ticket-content park. Rewrite every operator road that names `CHUPA_PLAN.md` or "the plan" to name the ticket only (the spent-cap road, the Reject road, and `_premise_road`, whose `source: seed` branch goes). Update the module docstring.
- In: `chupa/config.py`: delete the `caps.hardening` field.
- In: `chupa/caps.py`: `DECLARED_CAPS` keeps `"hardening"`, with a comment saying why: the journal holds 47 historical `hardening` draws and `audit` checks every draw against this list. Nothing draws it any more.
- In: `chupa/journal.py`: `Dispatch` keeps `"spec_gap_hold"` and `SIGNAL_NAMES` keeps `"hardening_round"`, each with a comment saying why: the journal holds 411 historical `spec_gap_hold` terminals and 47 rounds, and `dispatch_of` refuses unknown values. Readers treat `spec_gap_hold` like `escalate` (no special release).
- In: tests. Delete `tests/test_hardening.py`. In `tests/test_drain.py` delete `test_a_spec_gap_hold_waits_for_its_hardening_ticket_then_re_runs_free`, `test_a_spec_gap_hold_never_re_runs_while_its_hardening_ticket_is_unmerged`, `test_a_spec_gap_premise_releases_on_its_hardening_merge_without_a_ticket_edit`, `test_legacy_spec_gap_hold_without_round_is_released`, `test_plan_bound_arrival_is_never_auto_kept_and_releases_on_a_unit_change`, `test_plan_bound_premise_is_not_premise_parked`, `test_existing_bound_unit_releases_only_on_its_committed_bytes_change`, `test_retired_hardener_is_never_dispatched`, `test_plan_bound_legacy_hold_release_draws_retry_despite_spent_diagnosis`, `test_plan_bound_change_does_not_release_a_spent_retry`, `test_plan_in_worktree_but_not_head_does_not_abort_drain`, plus `round_record`/`bound_arrival` helpers if unused, and the `spec_gap` kinds of `test_pause_preserves_free_premise_and_spec_gap_reoffers`. In `tests/test_seed_path.py` delete `test_row_seed_without_its_entry_unit_files_a_hardening_ticket_and_holds`, `test_spent_hardening_cap_routes_the_stem_to_the_reject_queue`, `test_unchanged_units_after_a_closed_round_route_spec_gap_unresolved`, `test_structured_premise_spec_gap_files_a_round_for_its_unit`, `test_premise_naming_a_fact_a_complete_entry_unit_omits_files_hardening`, `test_reaped_filer_replays_its_round_commit`, `test_round_ticket_covers_all_gaps_with_the_filers_priority_and_deep_capability`, `test_roundless_unresolved_terminal_does_not_erase_unchanged_round_coverage`, `test_new_round_covers_only_gaps_not_unchanged_in_the_prior_round`, `test_operator_keep_starts_a_new_hardening_lineage`. In `tests/test_daemon_composition.py` drop the `"spec-gap"` case of the `change` parametrize. In `tests/test_drain_upgrade.py` delete `test_a_seed_stems_premise_road_names_the_plan_first` (it pins the plan road that `_premise_road` loses). In `tests/test_reject_queue.py` delete `test_confirm_after_a_plan_fix_of_a_bound_unit_is_not_a_double_confirm`. In `tests/test_closed_sets.py` drop the `hardening` import and `test_hardening_closed_sets_and_constants`. In `tests/test_config.py` drop `"hardening"` from the defaults.
- In: add `test_historical_spec_gap_hold_terminal_reads_without_release` to `tests/test_drain.py`: a stem whose last terminal is `{"to": "premise_failed", "dispatch": "spec_gap_hold", "round": 1, "plan_units": {...}}` is folded without error and is premise-parked like any other `premise_failed` (it fails if `dispatch_of` refuses the old value, or if the stem is released without a ticket edit).
- In: `docs/how-chupa-works.md`: delete the `hardening` row in section 6.4 and the spec-gap hardening bullet in section 13. `docs/host-contract.md`: drop `hardening` from both `caps` lists.
- This ticket overrides the `CLAUDE.md`/`AGENTS.md` rules that say plan defects are fixed in the plan: do not edit `CHUPA_PLAN.md`.
- Out: the seed review and its mechanical `spec_gap` findings in `chupa/stages.py`, `Finding.kind`/`unit`, ticket grammar, `CHUPA_PLAN.md`, the journal files.

## Scope fence
- chupa/hardening.py
- chupa/runner.py
- chupa/drain.py
- chupa/config.py
- chupa/caps.py
- chupa/journal.py
- tests/test_hardening.py
- tests/test_drain.py
- tests/test_seed_path.py
- tests/test_daemon_composition.py
- tests/test_reject_queue.py
- tests/test_drain_upgrade.py
- tests/test_closed_sets.py
- tests/test_config.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `grep -n -E "hold_on_hardening|file_hardening|awaited_hardening|plan_units|chupa.hardening|in CHUPA_PLAN\.md|in the plan|plan and regenerate|not the plan's" chupa/runner.py chupa/drain.py` prints nothing (it matches any hardening code or plan-naming operator road left; module-docstring citations are a later ticket's), and `chupa/hardening.py` does not exist.
2. A historical `spec_gap_hold` terminal still folds and parks like an ordinary premise failure, not released and not refused, checked by `uv run pytest tests/test_drain.py -k historical_spec_gap_hold`.
3. `docs/how-chupa-works.md` has no `hardening` cap row and no spec-gap hardening bullet.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain.py -k historical_spec_gap_hold
uv run pytest -q
```

## Definition of rejected
`CHUPA_PLAN.md` or any journal file changes; `spec_gap_hold`, `hardening_round`, or the `hardening` declared cap is removed from the readable vocabulary; the seed review changes.

## Time budget
- expected: 60m
- stuck: 90m
