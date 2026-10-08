---
priority: P0
kind: bug
agent_tier: high
agent_effort: high
source: human
state: confirmed
---

## Depends on
- hardening-round-records

## Context
- chupa/artifacts.py
- chupa/specs.py
- chupa/requisition.py
- chupa/stages.py
- chupa/runner.py
- tests/test_seed_path.py
- tests/test_requisition.py
- tests/test_hardening.py
- tests/test_stages.py

## Plan contract
- section 5
- section 7.3
- section 11.4
- 19.L

## Goal / Why
Spec gaps are detected from structured, validated fields and never from prose. A `Finding` carries a nullable `unit`. The seed path's mechanical SPEC DEPTH check runs over every hardenable unit of a seed, before grammar. The runner reads the gapped units from the run's own StageResult findings. The `premise` regex, the `checks.json` re-read, and NON-CONVERGENCE are deleted.

Why: section 11.4 DETECTION reads codes and records only, and section 5 makes `unit` a validated field never parsed from prose. Today `chupa/runner.py` `premise_spec_gaps` regex-matches `19.P<n>.<row>` in a premise's message and paved road. Any premise that mentions a unit id files a hardener, including code/seam contradictions a plan edit cannot fix. `spec_gaps` re-reads `tickets/<stem>/checks.json` from main instead of this run's Check result, files every seed `spec_gap` against the seed's OWN row whichever unit gapped, and treats changing finding wording over three passes as a spec gap. `chupa/stages.py` checks only the seed's own row unit, so a cited unit that is missing fails as an unresolvable `Plan contract` id (an `authoring_error`).

## Scope in / Scope out
- In (CONTRADICTED TESTS): `tests/test_hardening.py::test_a_hardener_is_never_hardened` monkeypatches the deleted `runner.spec_gaps` and `runner.premise_spec_gaps`; migrate it to inject each gap through this run's StageResult findings (`{kind: spec_gap, unit}`), keeping all four cases (gate_failed and premise_failed, hardener and non-hardener) as behavioral coverage.
- In (CONTRADICTED TESTS, recorded value): `tests/test_stages.py:302` pins the run record's `spec: implement 1.1`; update that recorded value to `implement 1.2` with the spec bump and change nothing else in that file.
- In: `chupa/artifacts.py` `Finding` gains `unit: str | None = None`. A validator refuses a non-null `unit` unless `kind == "spec_gap"`.
- In: `chupa/specs.py` gains `hardenable_units(plan, stem, plan_contract) -> tuple[str, ...]`: the stem's own entry unit when it is a non-exit registry row, plus every cited id that names an entry unit of a registry row. `entry_unit_gap` takes a unit id. Every caller is updated in place.
- In: `chupa/stages.py` `_review_one` runs the SPEC DEPTH check over every hardenable unit before `validate_ticket`. It reads the seed's `## Plan contract` bullets without resolving them. Each missing unit or part yields a snag finding `{code: requisition_review, kind: spec_gap, unit: <uid>}` with mechanical `entry unit gap`. The seed's hardenable units reach `review_ticket`.
- In: `chupa/requisition.py` validates each reply finding against the judged ticket's hardenable units. A `spec_gap` finding needs a `unit` from that set when the set is non-empty, and null otherwise. A violation takes the surface's existing schema-invalid path (`mechanical: invalid reply`). The implement surface validates `premise` findings the same way: `kind` is optional, and a `spec_gap` `unit` is checked against the ticket's hardenable units. A violation is a schema-invalid reply that takes the driver's existing re-prompt (section 5 invariant 2).
- In: `specs/requisition_review.md` (version `2.1`) asks for `unit` on every `spec_gap` finding, naming the ticket's own entry unit or a cited one. `specs/implement.md` (version `1.2`) allows an optional `kind` and `unit` on `premise` findings, and says a missing or under-specified governing unit is `kind: spec_gap` with that `unit`.
- In: `chupa/runner.py`. A Check `gate_failed` or an Implement `premise_failed` is a spec-gap terminal exactly when this run's StageResult findings hold `kind: spec_gap` with a non-null `unit`. The gapped units G are those units. `spec_gaps`, `premise_spec_gaps`, and the non-convergence fold are deleted. `IDENTICAL_K` stays for the identical-wall rule.
- Out: round records, the hold, plan-bound release, vocabulary closure, and the copy refusal.

## Scope fence
- chupa/artifacts.py
- chupa/specs.py
- chupa/stages.py
- chupa/requisition.py
- chupa/runner.py
- specs/requisition_review.md
- specs/implement.md
- tests/test_seed_path.py
- tests/test_requisition.py
- tests/test_specs.py
- tests/test_hardening.py
- tests/test_stages.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seed_path.py` exits 0. In it, `test_review_that_never_converges_is_a_spec_gap` is deleted. A new `test_premise_mentioning_a_unit_id_in_prose_is_an_ordinary_premise` writes a premise whose message names `19.P3.gamma-seed` but carries no `kind`. It asserts the ordinary premise park: a `premise_bounce` draw, no `hardening_round` record, and no `plan-gap-*` ticket. A new `test_structured_premise_spec_gap_files_a_round_for_its_unit` makes the seeding ticket's `## Plan contract` cite `19.P3.gamma-seed`, writes a premise `{kind: spec_gap, unit: 19.P3.gamma-seed}`, and asserts that the round's `units` hold exactly that unit. A new `test_cited_missing_unit_is_a_spec_gap_not_a_grammar_refusal` gives a seed whose `## Plan contract` cites `19.P3.gamma-seed`, a registry row with no entry-unit heading. It asserts a snag finding with `kind: spec_gap` and that `unit`, and no `requisition_review` call.
2. `uv run pytest -q tests/test_requisition.py` exits 0. It includes `test_spec_gap_finding_unit_is_validated`, in which a `spec_gap` finding with no `unit` or with a unit outside the hardenable set yields `mechanical: invalid reply`, while a valid unit passes through. The existing spec-key test also asserts that `` `unit` `` appears in `specs/requisition_review.md`.
3. `uv run pytest -q tests/test_specs.py` exits 0. It includes `test_hardenable_units_are_own_row_plus_cited_entry_units` and `test_spec_lint_accepts_the_implement_and_requisition_specs`.
4. `uv run pytest -q tests/test_stages.py tests/test_terminal.py tests/test_reject_queue.py tests/test_audit.py` exits 0 with those suites unchanged except the one recorded `spec: implement 1.2` value in `tests/test_stages.py`: a premise finding without `kind` stays valid.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_seed_path.py
uv run pytest -q tests/test_requisition.py
uv run pytest -q tests/test_specs.py
uv run pytest -q tests/test_stages.py tests/test_terminal.py tests/test_reject_queue.py tests/test_audit.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_seed_path.py -k test_premise_mentioning_a_unit_id_in_prose_is_an_ordinary_premise
```
- carries: tests/test_seed_path.py

## Definition of rejected
Reject the branch if any routing decision reads a finding's `message` or `paved_road` text, if gaps are read from a file instead of this run's StageResult, if a `spec_gap` finding can name a unit outside the judged ticket's hardenable units, or if the regression test passes on the merge base.

## Time budget
- expected: 90m
- stuck: 180m
