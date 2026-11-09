---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: rejected
---

## Depends on
- diagnose-spec-reachable-road-rule

## Context
- tests/unit/test_specs.py::test_review_spec_checks_docs

## On-demand
- chupa/specs/review.md
- chupa/specs/diagnose.md

## Goal / Why
In serve-live-verdicts attempt 1, Review proposed checking the legacy `ticket-plane/<stem>/confirmed/<request_id>` effect key so pre-upgrade confirms are never re-applied, and Diagnose told Implement to add it. In attempt 2 a second Review snagged that branch as a banned compatibility shim and the ticket went to the Reject queue after paid attempts. Neither `chupa/specs/review.md` nor `chupa/specs/diagnose.md` limits a paved road or a lesson to what the repo rules allow.

After this change Review never offers a compatibility shim, legacy-key lookup, or parallel path as a `paved_road`. When the defect is a real upgrade or replay hazard the ticket does not cover, Review still reports it through routes its current Output format supports: an `rma` finding coded `ticket`, or a note in the `summary` as a second problem for the operator to file. Diagnose drops or rewrites any review paved road that conflicts with the repo's rules or the ticket's Definition of rejected, and keeps the hazard as a finding to report.

## Scope in / Scope out
- In: `chupa/specs/review.md`. In `## Task`, after the Admissibility paragraph, add a rule containing the exact phrase "never a compatibility shim". It says a `paved_road` is never a compatibility shim, legacy-key lookup, or parallel path, and that a real upgrade or replay hazard the ticket does not cover is still reported, either as an `rma` finding coded `ticket` or in the `summary` as a second problem for the operator to file. Bump `version` from `1.4` to `1.5`.
- In: `chupa/specs/diagnose.md`. In `## Task`, after the paragraph beginning "Write concrete lessons", add a sentence containing the exact phrase "conflicts with the repo's rules". It says a lesson drops or rewrites any review paved road that conflicts with the repo's rules or the ticket's Definition of rejected, and still carries the hazard as a finding to report rather than silencing it. Bump `version` from `1.4` to `1.5`.
- In: `tests/unit/test_specs.py`: pin `review` at `1.5` in `test_review_spec_read_only` and `test_review_spec_checks_docs`, pin `diagnose` at `1.5` in the version tuple, and add a test asserting both exact phrases appear in their specs.
- In: `tests/integration/test_stages.py`: change the pinned review `spec_version` assertion at line 312 from `"1.4"` to `"1.5"`, keeping every other assertion.
- Out: engine code, verdict lists, Output format and On-failure sections, lesson limits, other sentences in either spec, and `eval/` fixtures.

## Scope fence
- chupa/specs/review.md
- chupa/specs/diagnose.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py

## Acceptance criteria
1. `chupa/specs/review.md` contains `never a compatibility shim` and `version: "1.5"`, not `1.4`.
2. `chupa/specs/diagnose.md` contains `conflicts with the repo's rules` and `version: "1.5"`, not `1.4`.
3. `tests/unit/test_specs.py` has a test that asserts both phrases and passes under `./dev.py test tests/unit/test_specs.py`; it fails on specs lacking either phrase, so a spec that lets a shim paved road stand is ruled out.
4. The new review text names `rma` and `second problem` as the routes for an uncovered hazard, so a rule that silences the hazard is ruled out; the test asserts the text contains `second problem`.
5. `tests/integration/test_stages.py` asserts `spec_version == "1.5"` and passes under `./dev.py test tests/integration/test_stages.py`; a stale `"1.4"` pin is ruled out.
6. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
./dev.py test
```

## Definition of rejected
The change edits engine code, tells Review to stop reporting upgrade or replay hazards, lets either spec still permit a shim, legacy-key, or parallel-path road, routes a hazard to a field the Output format lacks, or alters the Output format, On-failure, or lesson limits.

## Time budget
- expected: 10m
- stuck: 30m
