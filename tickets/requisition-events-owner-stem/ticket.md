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
- chupa/driver.py::Driver.run
- chupa/driver.py::Driver.begin_watch
- chupa/observe.py::recent_steps
- tests/unit/test_requisition_stage_events.py
- tests/regress_requisition_stage_events.py
- docs/how-chupa-works.md#10. State on disk

## On-demand
- tests/integration/test_requisition.py
- tests/integration/test_watch.py

## Goal / Why
Ticket `requisition-stage-events` (merged as 8a7d18d2) made `review_ticket` log `stage_start` and `stage_end` under `stem=stem`, the stem of the ticket text being reviewed. `review_ticket` has four callers, and only the drain's dispatch (`chupa/runner.py`) reviews a queued ticket:

- Rework (`chupa/rework.py`) reviews each split or replace proposal under the proposal's stem, from inside the running `rework` stage.
- Author (`chupa/author.py`) reviews each candidate ticket under the candidate's stem, from inside the running `author` stage.
- The `review` verb (`chupa/__main__.py`) reviews a ticket on its own, with `stem_slot=f"review-{stem}"`.

On 2026-11-11, `commit-lock`'s rework proposed splits, and Recent Steps showed Requisition steps for `git-factory`, `git-factory-harness`, `commit-lock-core`, `git-maker` and `commit-lock-held-by-git`. None of these stems has a ticket (see `evidence/requisition-events-evidence.log`). The operator asked why Requisition steps appear for tickets that are not in the queue.

A review nested inside author or rework is a gate of that stage, and that stage's own `stage_start` and `stage_end` already bracket it. When this ticket is done, `review_ticket` logs stage events only when it owns the watch (it begins its own watch because no stage is active on the driver). It logs them under `stem_slot`, the watch owner. The drain's dispatch is unchanged, because there `stem_slot == stem`. A nested review logs no stage events. A `review` verb run logs under `review-<stem>`.

## Scope in / Scope out
- In: `chupa/requisition.py::review_ticket`:
  - Logs `stage_start` and `stage_end` only when no stage was active on the driver at its first provider call, the same condition under which it calls `driver.begin_watch`.
  - The events carry `stem=stem_slot`. `attempt`, `surface`, `run_seq`, `outcome` and `calls` keep their current values and meaning.
- In: `chupa/observe.py`: in the snapshot's Recent Steps rows, a ticket-stem step whose `tickets/<stem>/` holds neither the stage file nor `ticket.md` gets `path` `None`, not a path to a missing file. `review-<stem>` rows need this.
- In: `docs/how-chupa-works.md`, section 10, the `engine.log` row: a requisition review run inside author or rework logs no stage events of its own, and a standalone review logs them under its watch owner.
- In: update the tests that pin `stem=stem`: `tests/unit/test_requisition_stage_events.py` (its fake driver has `_active=True`), `tests/integration/test_requisition.py::test_requisition_stage_events_in_engine_log`, and `tests/regress_requisition_stage_events.py`. Add the new reproducer `tests/regress_requisition_events_owner_stem.py`.
- Out:
  - Changing `stem_slot` values at any caller.
  - A shared Driver seam for stage events, which is ticket `stage-event-owner-stem`.
  - Check and merge stage events.
  - The extension's JavaScript.

## Scope fence
- chupa/requisition.py
- chupa/observe.py
- docs/how-chupa-works.md
- tests/unit/test_requisition_stage_events.py
- tests/integration/test_requisition.py
- tests/integration/test_watch.py
- tests/regress_requisition_stage_events.py
- tests/regress_requisition_events_owner_stem.py

## Acceptance criteria
1. `tests/unit/test_requisition_stage_events.py`:
   - With a fake driver whose `_active` is `None` (and a recording `begin_watch`), each existing outcome case still records exactly `stage_start` then `stage_end`, and both carry `stem` `"slot"` (the `stem_slot`), not `"actual"`.
   - A new case with `_active` set records no `stage_start` or `stage_end` for any outcome, not a pair under `"actual"`.
2. `tests/integration/test_requisition.py::test_requisition_stage_events_in_engine_log` asserts the two `engine.log` events carry `stem` `"different-slot"`, not `"one-thing"`.
3. `tests/integration/test_watch.py`: the snapshot's Recent Steps row for a `requisition_review` event under `stem` `review-x`, with no `tickets/review-x/` directory, has `path` `None`, not `tickets/review-x/ticket.md`.
4. `tests/regress_requisition_events_owner_stem.py` builds its own temporary repository, config and `FakeLLM` driver, and imports nothing from `tests/`. It calls `review_ticket` with `stem="candidate"` and `stem_slot="owner"` from inside an active `Driver.run` stage, the way `chupa/author.py` does through an `LlmStage` `review` hook. It prints `pass` only when `engine.log` has no `requisition_review` stage event and no stage event with `stem` `"candidate"`.
5. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
6. `./dev.py test` exits 0.

## Regression
```
uv run python tests/regress_requisition_events_owner_stem.py
```
- carries: tests/regress_requisition_events_owner_stem.py

## Verification
```
./dev.py test
```

## Definition of rejected
- A requisition review run inside author or rework writes a `stage_start` or `stage_end`.
- A standalone requisition review stops writing its `stage_start` and `stage_end` pair.
- The extension filters or rewrites step rows in JavaScript.

## Time budget
- expected: 30m
- stuck: 60m
