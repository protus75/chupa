---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- coverage-map

## Context
- chupa/requisition.py
- tests/test_requisition.py

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
On 2026-11-06 the pre-run review approved `serve-no-auto-triage` after searching only for the names being removed. Three files outside its fence relied on the removed behavior, and the full suite failed in them after implementation. A test that executes a fenced file's code is a candidate dependent whether or not it names a changed symbol, and the coverage map from `coverage-map` lists those tests mechanically.

After this change the review receives, as data, every test file outside the fence that executes code in a fenced file. It must account for each one: either the ticket fences it, or the review clears it with a reason. When the host declares a map and it is missing, the review snags instead of guessing.

## Scope in / Scope out
- In: `chupa/requisition.py`:
  - `review_ticket` takes a required keyword `coverage_map: Path | None`: the map file path, or None when the host declares no `review.coverage_map`.
  - Before the first model call, it computes the dependents: for each fenced path that is a key in the map's `files`, the listed test files not covered by the fence (a fence entry matches an equal path or a descendant). The result is sorted lines `<test file>: runs <fenced file>, ...`, or `none`; with `coverage_map` None it is `no coverage map configured`.
  - A declared map that is missing or not valid JSON with a `files` mapping returns a mechanical snag (no model call, like the render-headroom snag): code `coverage_map`, paved road `run ./dev.py covmap`.
  - The dependents go to the spec as a new data block `coverage_dependents`.
- In: `chupa/specs/requisition_review.md`: a `coverage_dependents` data block, and a Task rule: every listed test file must be either in the fence, or cleared in the summary with one sentence on why the ticket's change does not affect it; an unaccounted file is a `snag` finding naming it. Bump the spec version's minor number.
- In: the production callers pass the map path from config: `<state_dir>/coverage-map.json` when `config.review.coverage_map` is set, else None: `chupa/__main__.py` (`review`), `chupa/runner.py`, `chupa/author.py`, `chupa/rework.py`.
- In: tests that call `review_ticket` pass `coverage_map=None` unless they test it: `tests/test_requisition.py`, `tests/test_provider_cooldown_failover.py`, `tests/test_watchdog_activation.py`, `tests/test_rework.py`.
- In: `tests/test_requisition.py`: with an inline map, the rendered prompt lists an out-of-fence test file that runs a fenced file and omits one that is fenced; a declared but missing map snags with code `coverage_map` and makes no model call; None renders `no coverage map configured`.
- In: `docs/how-chupa-works.md`: section 8.4's `requisition_review.md` row or section 9.3 notes the coverage dependents input and the missing-map snag.
- Out: building or refreshing the map; measuring code run in child processes; Implement, Check, or Merge behavior; any new gate code outside the requisition review.

## Scope fence
- chupa/requisition.py
- chupa/specs/requisition_review.md
- chupa/__main__.py
- chupa/runner.py
- chupa/author.py
- chupa/rework.py
- tests/test_requisition.py
- tests/test_provider_cooldown_failover.py
- tests/test_watchdog_activation.py
- tests/test_rework.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_requisition.py` exits 0, including the three map cases in Scope in.
2. `grep -n "coverage_dependents" chupa/specs/requisition_review.md` prints the data block.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_requisition.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a declared but missing map lets the review reach the model;
- `review_ticket` gives `coverage_map` a default;
- the review approves while a listed dependent is neither fenced nor cleared, in a test that pins it.

## Time budget
- expected: 45m
- stuck: 135m
