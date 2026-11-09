---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: confirmed
---

## Depends on
- implement-spec-sequential-final-run

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/implement.md
- docs/how-chupa-works.md

## Goal / Why
Implement leaves docs that describe the changed behavior stale. In the retro/26 window, two of five merged tickets lost a full attempt to this. Review snagged remove-merge-hold because `docs/host-contract.md` 'Pending cutover contract' item 1 still mentioned supervised host merge confirms. Review snagged stop-at-boundary because the serve row in `docs/how-chupa-works.md` section 2.1 still said 'until `kill` or a signal'. `chupa/specs/review.md` already snags on stale `docs/` and `README.md` statements, but `chupa/specs/implement.md` has no matching step. The finding only appears after a paid Implement and Review round. This repeats declined box reports 000315 (and tombstone 000316), and recurs in a new window, so the earlier decline is reopened. After this change Task in the implement spec has a step before the commit step: search `docs/` and `README.md` for statements of the behavior the diff changes and update those that the diff makes false, in the same commit. The step guards against overcorrection: edit only statements the diff falsifies and only files inside `## Scope fence`. A stale statement in a file outside the fence is reported in `second_problems`, not edited.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: add the stale-docs step to Task, immediately before the commit step, and bump `version` to the next minor above its value at the base commit ("2.5" when drafted; sibling spec tickets may have bumped it since).
- In: `tests/unit/test_specs.py`: the implement version pins move to that new version, plus assertions that the step's phrases are in the spec's Task.
- In: `tests/integration/test_stages.py`: the `spec: implement` pin in the run-record assertion moves to that new version.
- In: `docs/how-chupa-works.md` section 4.2: one sentence stating that Implement updates docs statements the diff makes false, inside the scope fence.
- Out: Check code, `chupa/stages.py`, the Review spec, the packing-slip schema, every other spec, and any change to the fence rules.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/implement.md` is at a version one minor above its value at the base commit and its Task contains the phrases `statements of the behavior the diff changes`, `docs/` and `README.md`. `./dev.py test tests/unit/test_specs.py` asserts each phrase, which rules out the base spec that has no docs step.
2. The spec Task contains the exact sentence ``A stale statement in a file outside `## Scope fence` is reported in `second_problems`, not edited.`` and the phrase `makes false`. `./dev.py test tests/unit/test_specs.py` asserts both, which rules out a step that rewrites loosely related prose or edits docs outside the fence.
3. The run-record assertion pins the new `spec: implement` version. `./dev.py test tests/integration/test_stages.py` rules out a stale pin.
4. `docs/how-chupa-works.md` section 4.2 states that Implement updates documentation statements that the diff makes false, inside the scope fence, in the same commit.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The step tells Implement to edit docs outside `## Scope fence` or to rewrite statements the diff does not make false; the step is placed after the commit step; the sequential-run or base-red rules from the earlier implement spec tickets are weakened; the implement spec's major version changes; the packing-slip schema or finding codes change; any other spec changes.

## Time budget
- expected: 20m
- stuck: 45m
