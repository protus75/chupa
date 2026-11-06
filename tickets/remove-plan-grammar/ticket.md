---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- plan-off-serve-path
- remove-plan-text-tests

## Runs before
- remove-bootstrap-ingest

## Context
- chupa/watchdog.py
- docs/host-authoring.md
- docs/how-chupa-works.md

## On-demand
- chupa/tickets.py
- chupa/specs.py
- chupa/stages.py
- tests/test_tickets.py
- tests/test_specs.py
- tests/test_stages.py
- tests/test_watchdog.py

## Goal / Why
The ticket format still knows the bootstrap plan: a `## Plan contract` section whose ids resolve against `CHUPA_PLAN.md`, `CHUPA_PLAN.md#19.P<n>.<stem>` fence anchors that let a ticket edit one plan unit, a Context rule whose fix says to cite the plan, and a seed citation law. `chupa/specs.py` carries the plan resolver and a plan structure lint, and the watchdog hashes plan units. The plan is frozen history and nothing may edit or cite it. After this change the ticket format, the scope-fence gate, and the watchdog have no notion of a plan, and `CHUPA_PLAN.md` is an ordinary file no code reads.

## Scope in / Scope out
- In: `chupa/tickets.py`: delete `PLAN_FILE`, `read_plan`, `SEED_REFUSED_SECTIONS`, `_seed_cites`, the `## Plan contract` parsing, the fence-anchor branch, the Context rule refusing the plan file, the `plan` parameter of `parse_ticket`, and `Ticket.plan_contract`; drop `Plan contract` from `OPTIONAL_SECTIONS` (it becomes an unknown section). The Context rule refusing a prompt spec keeps its refusal, and its paved road becomes "list the spec under `## On-demand` and fence it". `validate_ticket` stops reading the plan. Update the module docstring.
- In: `chupa/specs.py`: delete `PlanContractError` and every definition from the `Plan contract resolver` section to the end of the file (`plan_id`, `resolve_plan_contract`, `unit_sha`, `without_unit`, `required_units`, `entry_unit_gap`, `registry_rows`, `lint_plan` and their constants and helpers); drop imports left unused; update the module docstring.
- In: `chupa/stages.py`: delete `Evidence.plan_main`/`plan_head`, the plan reads in `gather_safety_evidence`, the plan-file exemption and `_unit_confined` in `ScopeFenceGate`, and the plan imports.
- In: `chupa/watchdog.py`: `ScopeObservation` drops the `CHUPA_PLAN.md#` anchor branch and the `unit_sha` import; the `'#' not in prefix` filter goes.
- In: `eval/host_loop.py`, `eval/shakeout/bench.py`: stop writing and committing a `CHUPA_PLAN.md` in their temp hosts.
- In: delete `tests/test_plan_lint.py`, `tests/test_no_plan_host.py`, `tests/regress_no_plan_host.py` (with no plan reader left, "works without a plan" proves nothing).
- In: `tests/test_specs.py`: delete every test of the deleted functions (the `--- Plan contract resolver ---` block, `test_required_units_exclude_phase_rows`) and the `PLAN`/`SUB_PLAN` constants; `test_engine_source_never_spells_the_raw_delimiter` drops the deleted `tests/test_plan_lint.py` path.
- In: `tests/test_tickets.py`: the `VALID` fixture and `repo` fixture drop `## Plan contract` and the plan file; delete `test_context_citing_the_plan_is_refused_naming_plan_contract`, `test_unresolvable_plan_contract_section_is_refused`, `test_plan_contract_section_with_its_own_subsection_is_refused`, `test_seed_must_cite_build_laws_and_phase_unit_never_refused_sections`, `test_row_seed_cites_its_entry_unit_never_its_phase`, `test_fence_anchor_names_one_entry_unit_of_the_plan`, `seed_citing`, `ROW_PLAN`; `test_valid_ticket_validates_and_commits` drops its `plan_contract` assertion; add `test_plan_contract_section_is_unknown`: a new ticket with `## Plan contract` is refused as an unknown body section (it fails if the section is still accepted).
- In: `tests/test_stages.py`: delete `test_bare_numeric_plan_contract_bullet_is_refused_at_intake`, `test_scope_fence_admits_a_plan_edit_confined_to_its_anchored_unit`, `test_scope_fence_admits_a_plan_edit_confined_to_all_anchored_units`, and the `UNIT_MAIN`/`UNIT_HEAD` constants; `test_gather_safety_evidence_runs_no_verification` drops its plan anchor and `plan_main`/`plan_head` assertions; the `repo` fixture stops writing a plan file if nothing else needs it. Add `test_scope_fence_refuses_a_plan_edit`: a branch that changes `CHUPA_PLAN.md` outside `## Scope fence` fails `scope_fence` (it fails if plan edits are still exempt).
- In: `tests/test_watchdog.py`: `DetectorRig`'s observation drops the `CHUPA_PLAN.md#19.P4.owned` entry; `test_spend_resets_only_on_observed_scope_mutation` drops its plan-unit block.
- In: `tests/test_rework.py` `original`: stop writing the plan and adding `## Plan contract`. `tests/test_closed_sets.py`: update `OPTIONAL_SECTIONS` and `SECTIONS`. `tests/test_host_loop.py`: drop the `chupa.specs` plan imports left unused.
- In: `docs/host-authoring.md`: delete the "Host tickets omit `Plan contract`" line. `docs/how-chupa-works.md` section 13: delete the plan-pointers and plan-reads bullets.
- This ticket overrides the `CLAUDE.md`/`AGENTS.md` rules that treat `CHUPA_PLAN.md` as a spec: do not edit `CHUPA_PLAN.md`.
- In: `tests/test_closed_sets.py` `test_specs_closed_sets_and_constants`: also drop the `specs.CITABLE_SECTIONS`, `specs.ENTRY_PARTS`, `specs.MAX_ADMISSION_PAYLOADS`, `specs.PLAN_UNITS`, `specs.REFUSED_SECTIONS` and `tickets.SEED_REFUSED_SECTIONS` assertions.
- Out: `CHUPA_PLAN.md` itself, committed ticket files, `source: seed` validity, `Finding`, the journal.

## Scope fence
- chupa/tickets.py
- chupa/specs.py
- chupa/stages.py
- chupa/watchdog.py
- eval/host_loop.py
- eval/shakeout/bench.py
- tests/test_plan_lint.py
- tests/test_no_plan_host.py
- tests/regress_no_plan_host.py
- tests/test_specs.py
- tests/test_tickets.py
- tests/test_stages.py
- tests/test_watchdog.py
- tests/test_rework.py
- tests/test_closed_sets.py
- tests/test_host_loop.py
- docs/host-authoring.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `grep -rn -E "['\"]CHUPA_PLAN|PLAN_FILE|read_plan|resolve_plan_contract|Plan contract|plan_contract|unit_sha|registry_rows" chupa eval` prints nothing (module-docstring mentions of the plan are another ticket's).
2. A new ticket with `## Plan contract` is refused as an unknown section, and a branch editing `CHUPA_PLAN.md` outside its fence fails `scope_fence` (each test fails if the old exemption survives), checked by `uv run pytest tests/test_tickets.py tests/test_stages.py -k "plan_contract_section_is_unknown or scope_fence_refuses_a_plan_edit"`.
3. `docs/how-chupa-works.md` section 13 has no plan-pointers or plan-reads bullet.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_tickets.py tests/test_stages.py -k "plan_contract_section_is_unknown or scope_fence_refuses_a_plan_edit"
uv run pytest -q
```

## Definition of rejected
`CHUPA_PLAN.md` or any committed ticket file changes; `source: seed` stops being valid; any behavior outside the plan grammar, resolver, fence anchors, and watchdog anchors changes.

## Time budget
- expected: 60m
- stuck: 90m
