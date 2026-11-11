---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- stage-event-owner-stem

## Context
- chupa/requisition.py::review_ticket
- tests/unit/test_requisition_stage_events.py
- tests/regress_requisition_stage_events.py
- docs/how-chupa-works.md#10. State on disk

## On-demand
- tests/integration/test_requisition.py

## Goal / Why
Ticket `requisition-events-owner-stem` (merged as 45e5c3af) changed `review_ticket`'s `stage_start` and `stage_end` to carry `stem=stem_slot` instead of `stem=stem`. The drain's dispatch passes `stem_slot == stem`, so it is unaffected. The `review` verb (`chupa/__main__.py`) passes `stem_slot=f"review-{stem}"`, so `./dev.py review foo` now shows in Recent Steps as a step of a made-up `review-foo`, not as a step of ticket `foo` (see `evidence/review-verb-stem-evidence.txt`). The operator wants it to read like every other step: ticket `foo`, `Requisition start`, then `Requisition end (<outcome>)`.

`stem_slot` is the spool and watch key and stays as it is. When this ticket is done, a standalone requisition review logs its stage events under the reviewed ticket's `stem`. A review nested inside author or rework still logs none (the `owns_watch` guard from 45e5c3af stays).

## Scope in / Scope out
- In: `chupa/requisition.py::review_ticket`: `event_context` carries `stem=stem`, not `stem=stem_slot`. The `owns_watch` guard and every other field stay unchanged.
- In: `docs/how-chupa-works.md`, section 10, the `engine.log` row: "a standalone review logs them under its watch owner" becomes "a standalone review logs them under the reviewed ticket's stem".
- In: flip the tests that pin `stem_slot` keying: `tests/unit/test_requisition_stage_events.py` (`context` and its `stem` assertions), `tests/integration/test_requisition.py::test_requisition_stage_events_in_engine_log`, and `tests/regress_requisition_stage_events.py`.
- Out:
  - `stem_slot` values at any caller, and `begin_watch`'s owner.
  - The `owns_watch` guard and `tests/regress_requisition_events_owner_stem.py`.
  - The snapshot step-path fallback in `chupa/observe.py`.

## Scope fence
- chupa/requisition.py
- docs/how-chupa-works.md
- tests/unit/test_requisition_stage_events.py
- tests/integration/test_requisition.py
- tests/regress_requisition_stage_events.py

## Acceptance criteria
1. `tests/unit/test_requisition_stage_events.py`: with no stage active, each outcome case records `stage_start` then `stage_end` with `stem` `"actual"` (the reviewed stem), not `"slot"`. The recorded `begin_watch` owner is still `"slot"`. With a stage active, no stage events are recorded.
2. `tests/integration/test_requisition.py::test_requisition_stage_events_in_engine_log` asserts both `engine.log` events carry `stem` `"one-thing"`, not `"different-slot"`.
3. `tests/regress_requisition_stage_events.py` prints `pass` only when the two `requisition_review` events carry `stem` `"one-thing"` while `stem_slot` is `"slot"`.
4. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
5. `./dev.py test` exits 0.

## Regression
```
uv run python tests/regress_requisition_stage_events.py
```
- carries: tests/regress_requisition_stage_events.py

## Verification
```
./dev.py test
```

## Definition of rejected
- A `review` verb run logs a stage event whose `stem` is `review-<stem>`.
- A requisition review nested in author or rework logs a stage event.
- A caller's `stem_slot` changes.

## Time budget
- expected: 20m
- stuck: 45m
