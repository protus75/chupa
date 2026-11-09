---
state: confirmed
source: human
priority: P0
kind: feature
---

## Depends on
- none

## Context
- test-gate.toml
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs
- tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys
- docs/how-chupa-works.md#8.4 Prompt specs and the driver

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
Requisition review approved three tickets (`results-schema-2-reader`, `core-drift-preflight`, `review-lock-only-for-intake`) that added production code to a file with a per-file unit coverage floor in `test-gate.toml` while their Scope fence held no `tests/unit` file. Each then failed the unit coverage gate (`testreport.py` 10.96% vs 13%, `hostfiles.py` 16.39% vs 17%, `reconcile.py` 11.76% vs 12%) and spent retries, premise bounces and diagnoses before parking; no attempt could pass, because the fence forbade the only fix (Suggestion Box retro finding 000365, 2026-11-08). The review spec checks coverage-dependent test files but never asks whether the fence lets new code reach its unit floor.

After this change, requisition review snags such a ticket before it runs, naming the file and its floor, so the author fences a unit test file up front.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`. Add one bullet to the `snag` list in `## Task`, after the coverage-dependents bullet, saying: when Scope in adds statements or branches to a file listed with a floor above 0 under `[coverage.files]` in the repo's `test-gate.toml`, the fence must hold a `tests/unit` file whose named tests run the new lines; a missing one is a `snag` finding naming the file and its floor. The bullet contains the exact phrase "the fence must hold a `tests/unit` file".
  Bump the spec's `version` from `3.2` to `3.3`.
- In: `tests/unit/test_specs.py`: the pinned `requisition_review` version becomes `3.3`.
- In: `tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys`: also assert the spec contains that exact phrase.
- In: `docs/how-chupa-works.md` section 8.4: the `requisition_review.md` row also names the unit coverage floor check.
- Out: any change to `chupa/requisition.py` or the data blocks the reviewer receives (the reviewer reads `test-gate.toml` from the repo itself), any change to the covgate or `test-gate.toml` thresholds, and the `diagnose.md` advice on coverage failures (box item 000367).

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/requisition_review.md` contains the new bullet and `version: "3.3"`, not `3.2`.
2. `./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py` passes, with the test asserting the new rule text present (it fails on the unchanged spec).
3. `docs/how-chupa-works.md` section 8.4's `requisition_review.md` row names the unit coverage floor check.
4. `./dev.py test` passes.

## Verification
```
./dev.py test
```

## Definition of rejected
The change edits `chupa/requisition.py`, changes the data blocks the reviewer receives, or lowers any `test-gate.toml` threshold.

## Time budget
- expected: 15m
- stuck: 40m
