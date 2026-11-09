---
state: confirmed
source: human
priority: P0
kind: feature
---

## Depends on
- none

## Context
- tests/unit/test_specs.py
- tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
On 2026-11-08 `vscode-graph-segments` was parked twice by the requisition review. Its first version already said `renderGraph(graph, colors)` in one Scope-in bullet, but required the three-argument call `renderGraph(r.graph, COLOR[r.section], COLOR)` in another. The first review reported two other findings and missed this contradiction. The second review caught it, costing one extra edit, intake, review, and park cycle.

The requisition review prompt lists contradictions only between a criterion and merged code, or between two criteria. It never asks the reviewer to check statements inside the ticket against each other, such as a declared signature and a call to it. Unlike `review.md`, it also never says to report every defect in one reply. After this change, the prompt covers both, so the first review reports internal contradictions and every other finding together.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md` `## Task`:
  - Add this snag bullet after the existing contradiction bullet, verbatim: `- Two statements anywhere in the ticket cannot both hold, for example a declared signature and a call to it, or a named fixture and the result a criterion expects from it.`
  - Add this sentence after the snag bullet list, before `When a prior review is given`, verbatim: `Report every finding in this one reply; never stop at the first.`
  - Bump the frontmatter `version` from `"3.2"` to `"3.3"`.
- In: `tests/unit/test_specs.py`: change the `requisition_review` version pin from `"3.2"` to `"3.3"`.
- In: `tests/integration/test_requisition.py` `test_spec_loads_and_names_finding_keys`: assert that both new sentences are in the spec source.
- Out: every other spec, the review stage code, and `docs/how-chupa-works.md`. Its spec-table row ("checking an authored ticket is buildable") still describes the surface accurately.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## Acceptance criteria
1. `./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py` passes. `test_spec_loads_and_names_finding_keys` fails on the old spec, because neither new sentence is in it, and passes on the new one.
2. Reading `chupa/specs/requisition_review.md` shows `version: "3.3"` and both new sentences in `## Task`.

## Verification
```
./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py
```

## Definition of rejected
The change removes or rewords an existing snag bullet, or edits a file outside the fence.

## Time budget
- expected: 15m
- stuck: 40m
