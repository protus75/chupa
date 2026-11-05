---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/requisition.py
- docs/how-chupa-works.md

## On-demand
- specs/implement.md
- specs/requisition_review.md
- specs/diagnose.md
- chupa/stages.py
- chupa/specs.py

## Goal / Why
Every Implement, requisition-review, and Diagnose call is told to read or judge against `CHUPA_PLAN.md` (a "plan contract", plan sections, spec-gap units, seeding rules, "plan defect" RMAs). The plan is a frozen bootstrap record, not a spec, so these instructions steer models toward a document that no longer governs anything. After this change, none of the three prompts mentions the plan, seeding, spec gaps, or units. The engine stops injecting plan text and stops requiring or validating `kind`/`unit` on model replies. Its earlier premise failure (the full suite was red on main because a test parsed a ticket naming a deleted file) was fixed on main by `da13b247`.

## Scope in / Scope out
- In: `specs/implement.md`: delete the plan-contract data block and every mention of it; delete the seeding-ticket exception in Task step 1 and "except new seed ticket files" in step 4; delete "(section 11.7)"; delete the `kind`/`unit`/`spec_gap`/`authoring_error` paragraph in Output format. Keep its guidance as plain text: a ticket that contradicts merged code or is malformed, or whose `## Scope fence` lacks a path the criteria force, is a `premise` finding naming that file. Bump `version` to "2.0".
- In: `specs/requisition_review.md`: judge buildability against merged code only; delete the plan-contract data block, the phase-exit/seeding bullet, and the `kind`/`unit` rules and keys. `rma` means no edit of this ticket can make it buildable: the problem it targets does not exist in merged code, or its goal contradicts merged behavior it may not change. On-failure says the same. Bump `version` to "3.0".
- In: `specs/diagnose.md`: lessons cite the ticket or merged code, never "the plan". Bump `version` to "1.2". `eval/diagnose_report.json` is left as is (stale until the eval is re-run).
- In: `chupa/stages.py`: `implement_inputs` drops its `plan` parameter and `plan_contract` key; `implement_stage` drops `TicketImplementReply`, `hardenable_units`, and its `read_plan` call; `_review_one` stops passing `plan` to `review_ticket`.
- In: `chupa/requisition.py`: delete `validate_finding_units`, the `kind`-required check, and the `hardenable_units` context; drop the `plan` parameter from `review_ticket`, `base_render_chars`, and `_base_render`; drop `plan_contract` from the render inputs.
- In: `chupa/specs.py`: delete `hardenable_units` (no caller remains).
- In: `chupa/author.py`, `chupa/rework.py`: stop passing `plan=`; drop the now-unused `read_plan` imports.
- In: `tests/test_specs.py`: delete `test_hardenable_units_are_own_row_plus_cited_entry_units`, `test_phase_citing_ticket_hardens_every_row_of_its_phase`, `test_specs_name_every_hardenable_unit_kind`, and `test_implement_spec_defines_both_premise_kinds`; drop the `hardenable_units` assertions in `test_required_units_exclude_phase_rows`; update the pinned versions and the implement inputs tuple.
- In: `tests/test_requisition.py`: update the inputs tuple and the `kind`/`unit` key assertion; delete the three spec_gap unit tests (`test_spec_gap_finding_unit_is_validated`, `test_spec_gap_without_hardenable_units_requires_null`, `test_invalid_implement_spec_gap_unit_is_reprompted`); drop `plan=` and plan `""` arguments.
- In: `tests/test_stages.py`: delete `test_implement_renders_numeric_plan_contract_section`.
- In: `tests/test_watchdog_activation.py`, `tests/test_provider_cooldown_failover.py`: drop `plan=` from `review_ticket` calls.
- In: `docs/how-chupa-works.md` section 13: prompts no longer receive plan text; spec-gap hardening is now reached only through the seed review's mechanical entry-unit check.
- This ticket overrides the `CLAUDE.md`/`AGENTS.md` rules "The plan is the seed" and "Generated files" for this change: do not edit `CHUPA_PLAN.md`; it is history, not a spec to keep in step.
- Out: `Finding.kind`/`unit`, runner hardening, seed review logic, `## Plan contract` grammar and `resolve_plan_contract`, every other spec, `CHUPA_PLAN.md`, `eval/diagnose_report.json`.

## Scope fence
- specs/implement.md
- specs/requisition_review.md
- specs/diagnose.md
- chupa/stages.py
- chupa/requisition.py
- chupa/specs.py
- chupa/author.py
- chupa/rework.py
- tests/test_specs.py
- tests/test_requisition.py
- tests/test_stages.py
- tests/test_watchdog_activation.py
- tests/test_provider_cooldown_failover.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `grep -n -i -E "plan|seed|spec_gap|unit|19\.|section [0-9]" specs/implement.md specs/requisition_review.md specs/diagnose.md` prints nothing.
2. `grep -n -E "hardenable_units|validate_finding_units|\"plan_contract\"" chupa/stages.py chupa/requisition.py` and `grep -n hardenable_units chupa/specs.py` print nothing. (The `## Plan contract` grammar, `resolve_plan_contract`, and the seed review keep their own `plan_contract` text; later tickets remove them.)
3. `docs/how-chupa-works.md` section 13 states that prompts carry no plan text.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q
```

## Definition of rejected
`CHUPA_PLAN.md` changes; `Finding` changes; the runner's hardening path or the seed review's mechanical checks change; any spec other than the three named ones changes.

## Time budget
- expected: 45m
- stuck: 90m
